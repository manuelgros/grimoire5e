# Changelog — Unreleased

## Bug Fixes
- Fix sentences being garbled where one cross-reference sat inside another — Find Familiar's note about additional animal forms, 36 class features carrying the "optional class features" note (Bardic Versatility, Cantrip Versatility, Blessed Strikes, Harness Divine Power and the rest), several rules, and items including Mace of Smiting and Vicious Weapon all showed a mangled fragment with stray markup where a normal sentence belonged. Nested references now resolve from the inside out. **No `{@…}` markup is left anywhere in the app** — across every spell, monster, item, feat, rule and class feature from all 37 books
- Fix the spell save DC and attack modifier lines missing from class Spellcasting features — Wizard, Cleric, Druid, Bard, Sorcerer, Warlock, Paladin, Ranger, Artificer and the Eldritch Knight / Arcane Trickster all printed a raw data blob where the two formulae belong. They now read "Spell save DC = 8 + your proficiency bonus + your Intelligence modifier" as the books do
- Fix bulleted lists in rules losing their content — **Concentration** listed the things that break concentration as raw data instead of text, as did Cackle Fever, Sewer Plague and six other rules. Named bullets also lost their label, so **Long Rest** showed its benefits as unlabelled paragraphs instead of "Regain All HP.", "Ability Scores Restored." and so on
- Fix cross-reference markup showing through in section headings and named entries — e.g. Figurine of Wondrous Power, Bronze Griffon displayed `{@creature griffon||Bronze Griffon}` as its heading, and the Apparatus of Kwalish showed a stray `{@h}` in its claw attack
- Fix monster and item detail views dumping raw data instead of a table — the same fault previously fixed for feats turned out to affect **316 monsters** and **102 magic items**. Every monster whose Info tab lore includes a table (Aboleth, Aberrant Cultist, most dragons) and every item with a roll table (Alchemy Jug, Deck of Many Things, Amulet of the Planes, Ammunition of Slaying) printed a wall of Python-looking gibberish where the table belonged. All four detail views now share one table renderer
- Fix roll ranges in spell tables showing raw data — Reincarnate, Confusion, Chaos Bolt and Summon Lesser Demons printed `{'type': 'cell', 'roll': {…}}` instead of the d100 range. Reincarnate's race table now reads `01-04  Dragonborn` as the book does, with zero-padding preserved
- Fix tables inside rules losing their dice notation and caption — a rule's table showed the literal text `{@dice 1d4}` instead of `1d4`, and the table's title was dropped entirely
- Fix feat detail views dumping raw data instead of a table — any feat whose description contains a table (Living Shadow and Second Skin from the new Ravenloft book, but also Crafter in the 2024 Player's Handbook, Rune Shaper, Strixhaven Initiate, the Eberron dragonmark feats and 24 in total) printed a line of Python-looking gibberish beginning `{'type': 'table', …}` where the table should have been. Tables now render with aligned columns, a heading and a rule
- Fix feats showing "Prerequisite: None" when they do have one — 28 feats were affected, including Heavily Armored, Heavy Armor Master, Medium Armor Master and Moderately Armored from the 2014 Player's Handbook, Fighting Initiate from Tasha's, every dragonmark feat, and the new Ravenloft feats. Armor and weapon proficiency requirements, campaign settings ("Ravenloft campaign"), spellcasting features and dragonmark exclusivity are now all spelled out
- Fix the feat category showing an internal code — Ravenloft's Dark Gifts displayed as `DG` and Eberron's dragonmark feats as `D`, in the detail view, the Feats list and Quick Search alike. The Feats tab's Category filter also had no entry for Dark Gifts, so the Ravenloft feats could not be filtered at all; it is now built from the categories your installed books actually contain, so it never offers a choice that returns nothing
- Fix the `--import` summary mangling content type names — importing a custom source reported "3 statuss" and "1 monsters" instead of "3 statuses" and "1 monster", and referred to base items and legendary groups by their internal names
- Fix custom uploaded sources disappearing after using Manage Sources — applying changes there rewrote the installed-source list from the official checkboxes only, silently dropping every uploaded book. The content stayed on disk and the source was still listed under Settings during that session, but on the next launch its spells, monsters and items vanished from every tab and its toggle was gone from Settings. Uploaded sources are now preserved when applying changes, and removing one still removes it for good

## New Features
- **Ravenloft: The Horrors Within**: The new Ravenloft book is now available in Manage Sources. Installing it adds its 70 monsters (Azalin Rex, Ankhtepot, the Aberrant Death's Head and the rest) with their Info-tab lore, and seven subclasses — Artificer (Reanimator), Bard (College of Spirits), Cleric (Grave Domain), Ranger (Hollow Warden), Rogue (Phantom), Sorcerer (Shadow Sorcery) and Warlock (Undead Patron). Its 11 feats (Mist Walker, Touch of Death, Living Shadow, …) and two magic items (Ebonbane, Harkon's Bite) live in the shared data files; see below for how to pick those up.

- **Data updates**: Manage Sources has a new **Re-download All** button that refreshes every file for your installed books, picking up errata and newly added content. Until now downloaded files were never replaced, so content added to shared data files (feats, magic items, variant rules) stayed invisible on existing installs no matter how many times you reopened Manage Sources. Settings also shows a one-line notice when the app ships a newer 5etools release than your downloaded data. The notice is a purely local version comparison — Grimoire still makes no network requests unless you ask it to download something

## Other Changes
- Data is now fetched from 5etools v2.33.2 (was v2.25.0). New installs get the newer data for every book; existing installs can pick it up with **Manage Sources → Re-download All**
- Network failures during a download now report what actually went wrong ("Could not reach the 5etools mirror", or the HTTP status and URL) instead of a raw socket error like `[Errno 8] nodename nor servname provided`

---

# Changelog — v0.3.1

## Bug Fixes
- Fix the app failing to start at all on Python 3.11, 3.12 and 3.13 — v0.3.0 crashed with `NameError: name 'Optional' is not defined` before the window ever opened. Only Python 3.14 was unaffected, which is why the problem escaped the 0.3.0 release. Anyone who could not launch v0.3.0 should upgrade
- Fix the monster Info tab being empty for every monster — the lore files it reads were never included in the download list, so v0.3.0 always showed "No description available for this monster" no matter which books were installed. Descriptions are now fetched the next time you open Manage Sources, and cover every book that has them (Monster Manual 2014 and 2025, Volo's, Mordenkainen's, Fizban's, Bigby's, the adventures, and the rest). The 2024 Dungeon Master's Guide, the 2014 Player's Handbook and Xanathar's publish no monster lore, so monsters from those three books keep the placeholder
- Fix mundane items in custom uploaded sources being silently discarded — a book's `baseitem` entries (its ordinary weapons, armor, tools and gear) were documented as supported but never actually imported, so they appeared in neither the Items tab nor its filters. They are now imported alongside magic items, with their damage dice, armor class, strength requirement, stealth note and weapon properties
- Fix searching for a name containing a colon returning the wrong results — typing `Bigby: Hand` in a list view silently searched for `Hand` instead, because everything before the colon was treated as a type prefix. Only the real prefixes (`s:`, `m:`, `i:`, `f:`, `c:`, `r:`) are now stripped, and `c:` works in the list views as it already did in Quick Search

---

# Changelog — v0.3.0

## Bug Fixes
- Fix `grimoire --version` reporting 0.1.0 — the version is now read from the installed package, so it can't fall out of step with the release again
- Fix option lists in class features not being selectable — Fighting Styles, Eldritch Invocations, Metamagic, Battle Master Maneuvers, Artificer Infusions, Elemental Disciplines, Arcane Shots, Runes and Pact Boons were shown as plain grey text because references nested inside an option list were never turned into buttons. Every option is now a focusable link to its own detail view (e.g. Fighter → Fighting Style → Dueling)
- Fix option links missing entirely on 2024 features that point at a whole category instead of listing each choice — Fighting Style (Fighter, Paladin, Ranger), Eldritch Invocations, Metamagic, Combat Superiority, Martial Versatility, Sorcerous Versatility, Infusions Known and Epic Boon now list their options as links. Option lists are scoped to the feature's edition, so a 2014 feature no longer offers the 2024 reprints of the same options
- Fix nested cross-references to other class and subclass features never becoming links (47 more references across the class data, e.g. options that point at a subclass feature)
- Fix spellcasting monsters from older books (Monster Manual 2014, Icewind Dale, etc.) only showing their at-will spells — prepared and known spells are now listed by level with their slot counts (e.g. the Archmage's `1st level (4 slots): detect magic, identify, mage armor*, magic missile`), including spell-list footnotes and warlock-style level ranges
- Fix Spellcasting appearing under Actions instead of Traits for monsters from 2014-era books
- Fix redundant spell lines being repeated when the monster's spellcasting description already names those spells
- Fix daily spell uses showing an internal marker (`1e/day`) instead of `1/day each`, and list them highest-use-first as the books do
- Fix Armor Class showing `?` for summoned creatures whose AC is a formula (e.g. Aberrant Spirit's "11 + the level of the spell"), and showing raw markup for monsters wearing named armor (e.g. `{@item studded leather armor|PHB}`)
- Fix Alignment showing internal codes for monsters with a range of alignments (e.g. the Assassin now reads "any non-good alignment" instead of "Lawful NX Chaotic NY Evil") and for monsters with weighted alignments (Cloud Giant, Empyrean)
- Fix app crash when opening the detail view of monsters with weighted alignments (Cloud Giant, Empyrean, Draconic Spirit)
- Fix damage resistance and immunity lines showing doubled parentheses and dropping qualifiers such as "nonmagical"
- Fix nested tags in third-party sources leaking raw markup into spell lists (e.g. `{@cite Casting Times}`), and render the `{@hom}`, `{@hitYourSpellAttack}`, and `{@actSaveSuccessOrFail}` tags as readable text
- Fix common items (weapons, ammunition, tools, etc.) showing empty descriptions — items without flavor text now display their mechanical stats (damage dice, damage type, range, armor class, strength requirement, stealth note, and weapon properties)
- Fix weapon property codes showing raw codes with source suffixes (e.g. `V|XPHB`) instead of proper names — properties now display as full names (e.g. `Versatile`, `Finesse`, `Two-Handed`)
- Fix Back button missing in monster detail view

## New Features
- **Monster descriptions**: Monster detail view now has an Info tab showing the monster's lore and description text, loaded from 5etools fluff files. Monsters without available descriptions show a placeholder message.
- **Class Features tab**: New tab (Ctrl+6) surfacing all class and subclass features (Wild Shape, Warding Flare, Battle Master Maneuvers, Eldritch Invocations, etc.) with filters for Class, Subclass, Level, and Source. Optional / variant features from later books (e.g. Tasha's) are marked with a `[variant]` badge. Class feature files are tied to the book they come from — installing PHB (2014), PHB (2024), Tasha's, Xanathar's, Fizban's, Van Richten's, Explorer's Guide to Wildemount, Bigby's, DMG, or Forgotten Realms: Heroes of Faerun will pull in the corresponding class features the next time you open Manage Sources.
- **Class Features in Quick Search**: Class features are now included in the global Quick Search, with a new `c:` prefix to narrow results to class features only (e.g. `c: wild shape`).
- **Optional features (Fighting Styles, Invocations, Metamagic, and friends)**: Grimoire now loads 5etools' optional feature data and gives each option its own detail view showing its category, prerequisite (e.g. "Level 5 Warlock", "Pact of the Blade", "eldritch blast cantrip") and resource cost (e.g. "1 Superiority Die"). Options are reached by following the links inside the class feature that grants them. The data file is fetched the next time you open Manage Sources; custom uploaded sources that define their own optional features are picked up too.
- **Navigable cross-references**: When a class feature references related features (e.g. Oath of Vengeance pointing to its Spells and Vow of Enmity), those references render as focusable buttons. Click or press Enter on a reference to jump straight to the target feature. Esc returns directly to the list view; Back walks the chain one step at a time.

---

# Changelog — v0.2.0

## Bug Fixes
- Fix magic item descriptions showing raw `{=bonusAc}` / `{=bonusWeapon}` placeholders instead of actual bonus values (+1, +2, +3) for armor, weapons, shields, and ammunition
- Fix feats and rules detail view subtitles staying yellow regardless of selected theme — now correctly follow the active theme's label color like spells, monsters, and items do
- Fix monster action entries showing raw `{@h}` tag before average damage values (e.g. `{@h}28 (3d12 + 9)` now renders as `28 (3d12 + 9)`)
- Fix custom sources disappearing from all content tabs after downloading additional official sources via Manage Sources
- Fix custom source content not appearing in source filter dropdowns after downloading additional official sources
- Fix app crash when filtering monsters by type (e.g. Undead) — some monsters use a structured tag format (`{"tag": "...", "prefix": "..."}`) that caused an `AttributeError` in the type filter logic
- Other small Bug Fixes to improve performance

## New Features
- **Custom source upload**: Import any 5etools-format JSON source book directly in the app (Settings → Upload Source) or via `grimoire --import /path/to/file.json`. Uploaded sources appear in all content tabs (monsters, items, spells, etc.) and in source filter dropdowns alongside official sources.
- **Remove custom sources**: Settings → Remove Custom lets you delete previously uploaded sources and their data files.
- **Non-blocking import**: Uploading a large source file no longer freezes the app — a loading indicator is shown while the file is being processed in the background.

## Changes
- Default theme changed from `textual-dark` to `5e-tools` for fresh installations
- Setup wizard now uses the `5e-tools` theme
- Monster list: replaced Size filter with Environment filter; only monsters that have environment tags are shown when filtering by environment (not all sourcebooks include this data)
- Keyboard navigation improvements across all menus: arrow keys (left/right) navigate between buttons, Tab jumps directly out of the button row instead of cycling through all buttons, and relevant menus auto-focus the first item on open
