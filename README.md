# Grimoire 5e

A terminal UI for D&D 5th Edition reference material — spells, monsters, items, feats, and rules — all searchable and filterable without leaving your keyboard.

![PyPI](https://img.shields.io/pypi/v/grimoire5e)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

## Features

- **Quick Search** across all content types with `s:`, `m:`, `i:`, `f:`, `r:` prefixes
- **Spells** — filter by level, school, class, source; sort by name / level / school
- **Monsters** — filter by CR, type, environment, source; sort by name / CR / type
- **Items** — filter by type (weapon, armor, wondrous, potion, poison…), rarity, attunement
- **Feats** — filter by source
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
| Windows  | `%APPDATA%\grimoire5e\grimoire\` |

The selection can be later edited via the Settings tab

## Usage

```
grimoire                          # launch app (setup wizard on first run)
grimoire --manage-sources         # open source manager to add/remove books
grimoire --import /path/to/file.json  # import a custom source and exit
```

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| `Tab` / `Shift+Tab` | Navigate between filters |
| `↑` / `↓` | Move through the list |
| `Enter` | Open detail view |
| `/` | Focus search |
| `Esc` | Return to Quick Search |
| `Ctrl+1–7` | Jump to tab |
| `q` | Quit |

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
XGE · TCE · VGM · MTF · MPMM · FTD · BGG · VRGR · MOT · GGR · EGW · SCC · AI · BMT · PHB

**Adventures**
HotDQ · RoT · PotA · OotA · CoS · SKT · ToA · WDH · WDMM · BGDIA · IDRotF · WBtW · FRAiF

**Forgotten Realms**
FRHoF

## Legal

This tool downloads data from the [5etools-mirror-3](https://github.com/5etools-mirror-3/5etools-src) repository for personal use only. Grimoire 5e does not bundle any game content — all data is fetched at runtime from publicly available mirrors of D&D 5e material published under the [Creative Commons Attribution 4.0 license](https://creativecommons.org/licenses/by/4.0/) (for XPHB/2024 content) or used under fair use for personal reference.

**Only download content you legally own.**

## License

[MIT](LICENSE)
