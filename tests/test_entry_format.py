"""
Unit tests for the shared entry renderers.

Every case here is a bug that actually shipped. The expected values come from
5etools' own render.js / parser.js, not from what the code happens to do — if a
case fails, check the JS before changing the expectation.
"""

import pytest

from grimoire.views._entry_format import (
    TAG_DISPLAY_SEGMENT,
    format_ability_line,
    format_attributes,
    format_quote,
    format_roll_cell,
    format_table,
    strip_reference_tags,
    tag_display_text,
)

IDENT = lambda s: s  # noqa: E731 — tests pass text through unchanged


# ── reference tags: which pipe segment is the display text ───────────────────

@pytest.mark.parametrize("raw,expected", [
    # third segment
    ("{@creature Riding Horse||Horse}", "Horse"),
    ("{@item Holy Water (Flask)|PHB|holy water}", "holy water"),
    ("{@variantrule Hit Points|XPHB|Hit Point}", "Hit Point"),
    ("{@status concentration||concentrating}", "concentrating"),
    ("{@table Magic Item Values|XDMG|200 GP}", "200 GP"),
    # deeper segments
    ("{@card Aberration|Deck of Many More Things|BMT|Ace}", "Ace"),
    ("{@quickref Cover||3||three-quarters cover}", "three-quarters cover"),
    ("{@classFeature Rage|Barbarian|PHB|1|XPHB|Wrath}", "Wrath"),
    # no display segment present -> fall back to the name
    ("{@spell Fireball}", "Fireball"),
    ("{@spell Fireball|PHB}", "Fireball"),
    ("{@card Aberration|Deck of Many More Things|BMT}", "Aberration"),
    # tags that deliberately show the FIRST segment
    ("{@filter Abjuration or Illusion|spells|school=A;I|level=0}", "Abjuration or Illusion"),
    ("{@book mounted|PHB|9|Mounted Combat}", "mounted"),
    ("{@i italic text}", "italic text"),
    # several tags in one string
    ("a {@spell fireball|PHB|fire ball} and a {@creature Goblin||gob}",
     "a fire ball and a gob"),
])
def test_reference_tag_display_text(raw, expected):
    assert strip_reference_tags(raw) == expected


def test_empty_display_segment_falls_back_to_name():
    assert tag_display_text("creature", "Goblin||") == "Goblin"


def test_unknown_tag_defaults_to_first_segment():
    assert tag_display_text("somethingNew", "Name|src|other") == "Name"


def test_segment_table_matches_5etools():
    # Spot-check the values that differ from the common case; a wrong index here
    # silently renders a source code or a filter query to the user.
    assert TAG_DISPLAY_SEGMENT["spell"] == 3
    assert TAG_DISPLAY_SEGMENT["card"] == 4
    assert TAG_DISPLAY_SEGMENT["quickref"] == 5
    assert TAG_DISPLAY_SEGMENT["subclass"] == 5
    assert TAG_DISPLAY_SEGMENT["classFeature"] == 6
    assert TAG_DISPLAY_SEGMENT["subclassFeature"] == 8
    assert "filter" not in TAG_DISPLAY_SEGMENT  # shows its first segment


# ── table roll cells ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("cell,expected", [
    ({"type": "cell", "roll": {"exact": 1}}, "1"),
    ({"type": "cell", "roll": {"min": 2, "max": 6}}, "2-6"),
    ({"type": "cell", "roll": {"min": 1, "max": 4, "pad": True}}, "01-04"),
    ({"type": "cell", "roll": {"exact": 7, "pad": True}}, "07"),
    # an explicit entry wins over the roll
    ({"type": "cell", "roll": {"exact": 1}, "entry": "Ace of hearts"}, "Ace of hearts"),
    ({"type": "cell", "entry": "no roll"}, "no roll"),
    # open-ended range
    ({"type": "cell", "roll": {"min": 90, "max": 100000000000000000000}}, "90+"),
    # display overrides
    ({"type": "cell", "roll": {"min": 1, "max": 9, "displayMax": 10}}, "1-10"),
    ({"type": "cell"}, ""),
])
def test_roll_cell(cell, expected):
    assert format_roll_cell(cell, IDENT) == expected


# ── tables ───────────────────────────────────────────────────────────────────

def test_table_aligns_and_keeps_caption():
    table = {
        "type": "table",
        "caption": "Shadow's Will",
        "colLabels": ["1d8", "Behavior"],
        "rows": [["1", "Move randomly."], ["2-6", "Do nothing."]],
    }
    out = format_table(table, IDENT, "yellow")
    lines = out.split("\n")
    assert "Shadow's Will" in lines[0]
    assert lines[-2].startswith("1   ")   # short column padded
    assert lines[-1].startswith("2-6 ")
    assert "Do nothing." in lines[-1]


def test_table_renders_dict_cells_not_raw_dicts():
    table = {
        "type": "table",
        "colLabels": ["d100", "Race"],
        "rows": [[{"type": "cell", "roll": {"min": 1, "max": 4, "pad": True}}, "Dragonborn"]],
    }
    out = format_table(table, IDENT, "yellow")
    assert "01-04" in out
    assert "{'type'" not in out


def test_table_delegates_unknown_cells_to_caller():
    # Cells can hold a whole nested entries block; without the render callback
    # they used to be stringified into a raw dict on screen.
    table = {
        "type": "table",
        "rows": [["1", {"type": "entries", "name": "Dread", "entries": ["Spooky."]}]],
    }
    out = format_table(table, IDENT, "yellow", render=lambda e: f"<{e['name']}>")
    assert "<Dread>" in out
    assert "{'type'" not in out


def test_table_skips_malformed_rows():
    table = {"type": "table", "colLabels": ["a"], "rows": [["ok"], {"type": "row"}]}
    assert "ok" in format_table(table, IDENT, "yellow")


# ── quotes ───────────────────────────────────────────────────────────────────

def test_quote_keeps_attribution():
    out = format_quote(
        {"type": "quote", "entries": ["Words."], "by": "Mordenkainen"}, IDENT, IDENT
    )
    assert "Words." in out
    assert "Mordenkainen" in out


def test_quote_combines_by_and_from():
    out = format_quote(
        {"type": "quote", "entries": ["Words."], "by": "X", "from": "Y"}, IDENT, IDENT
    )
    assert "X, Y" in out


def test_quote_without_attribution_has_no_dash():
    out = format_quote({"type": "quote", "entries": ["Words."]}, IDENT, IDENT)
    assert "—" not in out


# ── spellcasting ability lines ───────────────────────────────────────────────

def test_ability_dc_line():
    out = format_ability_line(
        {"type": "abilityDc", "name": "Spell", "attributes": ["int"]}, "yellow"
    )
    assert "Spell save DC" in out
    assert "8 + your proficiency bonus + your Intelligence modifier" in out


def test_ability_attack_mod_line():
    out = format_ability_line(
        {"type": "abilityAttackMod", "name": "Spell", "attributes": ["wis"]}, "yellow"
    )
    assert "Spell attack modifier" in out
    assert "your proficiency bonus + your Wisdom modifier" in out


@pytest.mark.parametrize("attrs,expected", [
    (["int"], "Intelligence modifier"),
    (["spellcasting"], "spellcasting ability modifier"),
    (["str", "dex"], "Strength or Dexterity modifier (your choice)"),
])
def test_format_attributes(attrs, expected):
    assert format_attributes(attrs) == expected
