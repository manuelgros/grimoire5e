"""
Corpus tests: render every entry of every downloaded book and assert the output
is clean.

These are the checks that found the rendering bugs fixed in this release. They
run against whatever books are installed, so the more you have downloaded the
more they cover. Run them after bumping the pinned 5etools tag in sources.json —
a new book can introduce an entry type no view has a branch for.

Three distinct failure modes are covered, because each hides from the others:

  raw dicts     an unhandled entry type stringified onto the screen
  stray tags    a {@tag} that no _strip_tags pattern matched
  dropped data  output that reads fine but silently lost a field
"""

import json
import re

import pytest
from rich.text import Text

from grimoire.views._entry_format import strip_reference_tags
from grimoire.views.feat_detail import FeatDetailScreen
from grimoire.views.feature_detail_base import FeatureDetailScreen
from grimoire.views.item_detail import ItemDetailScreen
from grimoire.views.monster_detail import MonsterDetailScreen
from grimoire.views.rules import RuleDetailScreen
from grimoire.views.spell_detail import SpellDetailScreen

RAW_DICT = re.compile(r"\{'[a-zA-Z_]+':|\[\{'")
STRAY_TAG = re.compile(r"\{@\w+")
MONSTER_BLOCKS = ("trait", "action", "bonus", "reaction", "legendary", "fluff")


def _screen(cls):
    """A detail screen detached from the app, so no Textual runtime is needed."""

    class Detached(cls):
        def __init__(self):
            pass

        def _label_color(self):
            return "yellow"

        def _section_color(self):
            return "cyan"

    return Detached()


def _widget_text(widget):
    rendered = widget.render()
    return rendered.plain if hasattr(rendered, "plain") else str(rendered)


def _rendered_blocks(loader):
    """Yield (label, markup) for everything the app can display."""
    spell = _screen(SpellDetailScreen)
    for x in loader.spells:
        if x.entries:
            yield f"spell {x.name} ({x.source})", spell.format_entries(x.entries)

    item = _screen(ItemDetailScreen)
    for x in loader.items:
        if x.entries:
            item.item = x
            yield f"item {x.name} ({x.source})", item._format_entries(x.entries)

    monster = _screen(MonsterDetailScreen)
    for x in loader.monsters:
        for attr in MONSTER_BLOCKS:
            entries = getattr(x, attr, None)
            if not entries:
                continue
            colours = (
                {"header_color": "cyan", "label_color": "yellow"}
                if attr == "fluff"
                else {}
            )
            yield (
                f"monster {x.name} ({x.source}).{attr}",
                monster._format_entries(entries, **colours),
            )

    feat = _screen(FeatDetailScreen)
    for x in loader.feats:
        if x.entries:
            yield f"feat {x.name} ({x.source})", feat._format_entries(x.entries)

    rule = _screen(RuleDetailScreen)
    for x in loader.rules:
        if x.entries:
            text = "\n".join(_widget_text(w) for w in rule._render_entries(x.entries))
            yield f"rule {x.name} ({x.source})", text

    feature = _screen(FeatureDetailScreen)
    for collection, kind in ((loader.classfeatures, "classfeature"),
                             (loader.optionalfeatures, "optionalfeature")):
        for x in collection:
            if x.entries:
                yield f"{kind} {x.name} ({x.source})", feature._format_entries(x.entries)


@pytest.fixture(scope="session")
def blocks(loader):
    rendered = list(_rendered_blocks(loader))
    assert rendered, "loader produced nothing to render"
    return rendered


def test_no_raw_dicts_reach_the_screen(blocks):
    """An entry type with no branch falls through to str() and dumps a dict."""
    offenders = [name for name, text in blocks if RAW_DICT.search(text)]
    assert not offenders, (
        f"{len(offenders)} blocks rendered a raw Python dict, e.g. {offenders[:5]}"
    )


def test_no_unrendered_tags(blocks):
    """Every {@tag} must be resolved, including tags nested inside other tags."""
    offenders = [name for name, text in blocks if STRAY_TAG.search(text)]
    assert not offenders, (
        f"{len(offenders)} blocks kept 5etools markup, e.g. {offenders[:5]}"
    )


def test_markup_parses(blocks):
    """Bracket characters in source text must not produce invalid Rich markup."""
    offenders = []
    for name, text in blocks:
        try:
            Text.from_markup(text)
        except Exception as exc:  # noqa: BLE001 — any parse failure is a bug
            offenders.append((name, str(exc)[:60]))
    assert not offenders, f"invalid markup, e.g. {offenders[:3]}"


# Fields that are easy to drop because the type renders "fine" without them.
DROPPABLE = [("itemSub", "name"), ("inset", "name"), ("quote", "by"), ("quote", "from")]


def _collect(node, wanted, found):
    if isinstance(node, dict):
        if node.get("type") == wanted:
            found.append(node)
        for key, value in node.items():
            if key in ("entries", "items", "entry", "rows"):
                _collect(value, wanted, found)
    elif isinstance(node, list):
        for value in node:
            _collect(value, wanted, found)


def test_no_silently_dropped_fields(loader):
    """
    Output that looks clean can still have lost data.

    A beholder's eye rays rendered as unbroken prose because `itemSub` names were
    discarded — no raw dict, no stray tag, just missing content.
    """
    sources = {
        "spell": (loader.spells, ["entries"], _screen(SpellDetailScreen).format_entries),
        "feat": (loader.feats, ["entries"], _screen(FeatDetailScreen)._format_entries),
        "classfeature": (
            loader.classfeatures, ["entries"], _screen(FeatureDetailScreen)._format_entries
        ),
        "monster": (
            loader.monsters, list(MONSTER_BLOCKS), _screen(MonsterDetailScreen)._format_entries
        ),
    }
    offenders = []
    for kind, (collection, attrs, render) in sources.items():
        for obj in collection:
            for attr in attrs:
                entries = getattr(obj, attr, None)
                if not entries:
                    continue
                text = render(entries)
                for wanted, field in DROPPABLE:
                    found = []
                    _collect(entries, wanted, found)
                    for node in found:
                        value = node.get(field)
                        if not value:
                            continue
                        # The field's own tags get resolved on the way out, so
                        # compare the resolved form rather than the raw source.
                        expected = strip_reference_tags(str(value))
                        if expected not in text:
                            offenders.append(
                                f"{kind} {obj.name}: {wanted}.{field}={value!r}"
                            )
    assert not offenders, (
        f"{len(offenders)} fields were dropped from rendered output, "
        f"e.g. {offenders[:5]}"
    )


def test_every_entry_type_has_a_branch(loader):
    """
    Fail loudly when a book introduces an entry type nothing handles.

    Passing this does not prove the type renders *well* — check what other keys
    it carries before deciding a branch is unnecessary.
    """
    known = {
        # structural
        "list", "item", "itemSub", "entries", "section", "table", "cell", "row",
        "inset", "insetReadaloud", "quote", "options",
        # rendered by a dedicated branch
        "abilityDc", "abilityAttackMod", "abilityGeneric", "statblock",
        "refClassFeature", "refSubclassFeature", "refOptionalfeature", "refFeat",
        # carry no displayable text of their own
        "image", "gallery", "link", "internal", "external", "hr", "spellcasting",
        "itemSpell", "flowchart", "flowBlock", "variant", "variantSub", "inline",
        "inlineBlock", "bonus", "bonusSpeed", "dice", "actions", "attack",
    }
    seen = {}

    def walk(node, owner):
        if isinstance(node, dict):
            kind = node.get("type")
            if kind:
                seen.setdefault(kind, owner)
            for key, value in node.items():
                if key in ("entries", "items", "entry", "rows"):
                    walk(value, owner)
        elif isinstance(node, list):
            for value in node:
                walk(value, owner)

    for collection, attrs in (
        (loader.spells, ["entries"]), (loader.items, ["entries"]),
        (loader.feats, ["entries"]), (loader.rules, ["entries"]),
        (loader.classfeatures, ["entries"]), (loader.optionalfeatures, ["entries"]),
        (loader.monsters, list(MONSTER_BLOCKS)),
    ):
        for obj in collection:
            for attr in attrs:
                walk(getattr(obj, attr, None), f"{obj.name} ({obj.source})")

    unknown = {k: v for k, v in seen.items() if k not in known}
    assert not unknown, (
        "unhandled entry types found — add a branch or add to the known set "
        f"after checking what fields they carry: {json.dumps(unknown, indent=2)}"
    )
