# Grimoire 5e

A terminal UI for D&D 5th Edition reference material — spells, monsters, items, feats, class features, and rules — all searchable and filterable without leaving your keyboard.

![PyPI](https://img.shields.io/pypi/v/grimoire5e)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

## Features

- **Quick Search** across all content types with `s:`, `m:`, `i:`, `f:`, `c:`, `r:` prefixes
- **Spells** — filter by level, school, class, source, concentration and ritual; sort by name / level / school
- **Monsters** — filter by CR, type, environment, source; sort by name / CR / type; lore on the Info tab
- **Items** — filter by type (weapon, armor, wondrous, potion, poison…), rarity, attunement, source
- **Feats** — filter by category (general, origin, fighting style, epic boon) and source
- **Class Features** — every class and subclass feature, filterable by class, subclass, level and source, with selectable links to the options they grant (Fighting Styles, Eldritch Invocations, Metamagic, Maneuvers, Infusions…)
- **Rules** — conditions, status effects, diseases, and core rules from XPHB
- **Themes** — Classic D&D, 5e Tools, Arcane, Parchment, Gelatinous Cube (+ Textual built-ins)
- **Manage Sources** in-app — download new books or toggle active ones without restarting
- **Custom source upload** — import third-party or homebrew books in 5etools format
- Supports **30+ official sourcebooks** including adventures and Forgotten Realms titles

## Requirements

- Python 3.11 or newer
- Internet connection for first-run data download
- **Windows only:** [Windows Terminal](https://aka.ms/terminal) (the default CMD/PowerShell console does not support the required ANSI colours)

## Installation

### Recommended (pipx)

[pipx](https://pipx.pypa.io) installs Python CLI tools in isolated environments and puts them on your PATH — no virtual environment management needed.

```bash
# macOS
brew install pipx && pipx install grimoire5e

# Linux (Debian/Ubuntu)
apt install pipx && pipx install grimoire5e

# Windows (in Windows Terminal, using winget)
winget install Python.Launcher
pip install pipx
pipx install grimoire5e
```

### Alternative (pip)

```bash
pip install grimoire5e
```

### From source (for development)

```bash
git clone https://github.com/manuelgros/grimoire5e.git
cd grimoire5e
pip install -e .
```

## First Run

On first launch, Grimoire opens a setup wizard where you select which source books to download. Only books you legally own should be selected.

```bash
grimoire
```

Data is downloaded from the public [5etools mirror](https://github.com/5etools-mirror-3/5etools-src) and stored in your platform's user data directory:

| Platform | Path |
|----------|------|
| macOS    | `~/Library/Application Support/grimoire/` |
| Linux    | `~/.local/share/grimoire/` |
| Windows  | `%LOCALAPPDATA%\grimoire5e\grimoire\` |

Downloaded books live in a `data/` subfolder there, alongside a `config.json` holding your theme and installed-source list.

The selection can be later edited via the Settings tab, which is also where you switch themes.

## Upgrading

Rerunning the install command does **not** upgrade an existing installation — `pip install grimoire5e` reports "requirement already satisfied" and `pipx install grimoire5e` refuses because the package is already there. Use the upgrade form instead:

```bash
pipx upgrade grimoire5e          # if you installed with pipx
pip install --upgrade grimoire5e # if you installed with pip
```

Check the result with:

```bash
grimoire --version
```

### After upgrading: refresh your sources

Upgrading replaces the program but never touches your downloaded books, so nothing you already have is re-downloaded. New releases sometimes need **additional data files** for the features they add, and those files are only fetched when you next visit the source manager.

Open **Settings → Manage Sources** (or run `grimoire --manage-sources`), leave your book selection exactly as it is, and choose Apply. Only genuinely missing files are downloaded — files already on disk are skipped — so applying an unchanged selection is quick and safe.

Skipping this step is harmless but leaves newer features without their data. Upgrading from v0.2.0 to v0.3.0, for example, an empty Class Features tab or option lists reading "None available" means the class feature and optional feature files haven't been downloaded yet.

### Getting updated data for books you already have

Apply only fetches files you're missing. When a release points at a newer 5etools snapshot — for errata, or for content added to shared files like feats and magic items — the books on your disk stay as they were. Settings shows a notice when this applies to you.

To update them, open **Settings → Manage Sources** and choose **Re-download All**. This replaces every file for your selected books, so it takes noticeably longer than Apply. Uploaded custom sources are never touched.

The notice is a local version comparison between the app and your data; it makes no network request. Grimoire only goes online when you download something.

## Uninstalling

```bash
pipx uninstall grimoire5e   # or: pip uninstall grimoire5e
```

Your downloaded books are stored outside the package and are **not** removed by uninstalling — deliberately, so reinstalling doesn't mean downloading everything again. To reclaim the space (typically tens of megabytes), delete the data directory listed under [First Run](#first-run).

## Usage

```
grimoire                          # launch app (setup wizard on first run)
grimoire --manage-sources         # open source manager to add/remove books
grimoire --import /path/to/file.json  # import a custom source and exit
```

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| `←` / `→` | Move between the filter dropdowns |
| `Tab` | Leave the filter row for the results list |
| `Shift+Tab` | Leave the filter row for the search box |
| `↑` / `↓` | Move through the list |
| `Enter` | Open detail view |
| `/` | Focus search |
| `Esc` | Close a detail view, or return to Quick Search |
| `Ctrl+1–8` | Jump to tab |
| `q` | Quit |

In a detail view, `↑` / `↓` scroll the text and `Tab` reaches the Back button. Where a feature links to related content (a class feature's options, for instance), `Enter` follows the link; `Esc` then returns straight to the list, while Back retraces one step at a time.

## Custom Sources

Grimoire can import third-party sourcebooks, adventures, or homebrew content as long as they are in the **5etools monolithic JSON format** — a single `.json` file with all content under top-level keys.

### Importing

**In-app:** Settings tab → **Upload Source** → enter the full path to your JSON file → Validate → Confirm Import.

**CLI (no UI):**
```bash
grimoire --import "/path/to/FleeMortals.json"
```

The source is split into per-type files and stored in the data directory. It then appears in all content tabs and source filter dropdowns alongside official sources — no restart required.

### Managing custom sources

Custom sources appear in the Settings tab source grid with a `(custom)` label. To remove one:

Settings tab → **Remove Custom** → check the sources to delete → Remove Selected.

This deletes both the data files and the registration entry. The source will disappear from all tabs immediately.

### Expected file format

Your JSON file must be a 5etools-format "data bundle" — a single object with one or more of these top-level keys:

| Key | Content |
|-----|---------|
| `spell` | Array of spell objects |
| `monster` | Array of monster stat blocks |
| `item` | Array of magic items |
| `baseitem` | Array of mundane/base items |
| `magicvariant` | Array of magic variant items (e.g. +1 weapons) |
| `feat` | Array of feats |
| `optionalfeature` | Array of optional features (Fighting Styles, Invocations, Metamagic…) |
| `condition` | Array of conditions |
| `disease` | Array of diseases |
| `status` | Array of status effects |

Keys that are absent or empty are silently skipped — you don't need all of them.

### What to watch out for

- **`source` field is required** on every object. All items must share a consistent source code (e.g. `"FM"` for Flee, Mortals!). Grimoire uses this to register and filter the source — objects with inconsistent or missing source codes may not appear.
- **Source code must be unique.** If you import a file whose source code matches an already-registered custom source, the existing files will be silently overwritten.
- **Official source codes are reserved.** Do not use codes like `PHB`, `DMG`, `XMM`, etc. — they will conflict with downloaded official data.
- **`name` field is required** on every object.
- Magic variant items (`magicvariant`) use `{=fieldName}` placeholders in their entries (e.g. `{=bonusAc}`) — these are resolved automatically from the `inherits` block, so no special handling is needed in your file.
- Grimoire does not validate or reformat your JSON beyond reading the supported keys. If an object is missing required fields (name, source) it will be skipped during load without an error message.

## Supported Sources

**Core (2024)**
XPHB · XDMG · XMM

**Core (2014)**
PHB · DMG · MM

**Supplements**
XGE · TCE · VGM · MTF · MPMM · FTD · BGG · VRGR · RHW · MOT · GGR · ERLW · EGW · SCC · BAM · AI · BMT

**Adventures**
HotDQ · RoT · PotA · OotA · CoS · SKT · ToA · WDH · WDMM · BGDIA · IDRotF · WBtW · FRAiF

**Forgotten Realms**
FRHoF

Full book titles for these codes are listed in **Settings → Manage Sources**.

## Legal

This tool downloads data from the [5etools-mirror-3](https://github.com/5etools-mirror-3/5etools-src) repository for personal use only. Grimoire 5e does not bundle any game content — all data is fetched at runtime from publicly available mirrors of D&D 5e material published under the [Creative Commons Attribution 4.0 license](https://creativecommons.org/licenses/by/4.0/) (for XPHB/2024 content) or used under fair use for personal reference.

**Only download content you legally own.**

## License

[MIT](LICENSE)
