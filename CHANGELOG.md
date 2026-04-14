# Changelog Draft — v0.3.0

## Bug Fixes
- Fix common items (weapons, ammunition, tools, etc.) showing empty descriptions — items without flavor text now display their mechanical stats (damage dice, damage type, range, armor class, strength requirement, stealth note, and weapon properties)
- Fix weapon property codes showing raw codes with source suffixes (e.g. `V|XPHB`) instead of proper names — properties now display as full names (e.g. `Versatile`, `Finesse`, `Two-Handed`)
- Fix Back button missing in monster detail view

## New Features
- **Monster descriptions**: Monster detail view now has an Info tab showing the monster's lore and description text, loaded from 5etools fluff files. Monsters without available descriptions show a placeholder message.
- **Class Features tab**: New tab (Ctrl+6) surfacing all class and subclass features (Wild Shape, Warding Flare, Battle Master Maneuvers, Eldritch Invocations, etc.) with filters for Class, Subclass, Level, and Source. Optional / variant features from later books (e.g. Tasha's) are marked with a `[variant]` badge. Class feature files are tied to the book they come from — installing PHB (2014), PHB (2024), Tasha's, Xanathar's, Fizban's, Van Richten's, Explorer's Guide to Wildemount, Bigby's, DMG, or Forgotten Realms: Heroes of Faerun will pull in the corresponding class features the next time you open Manage Sources.
- **Class Features in Quick Search**: Class features are now included in the global Quick Search, with a new `c:` prefix to narrow results to class features only (e.g. `c: wild shape`).
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
