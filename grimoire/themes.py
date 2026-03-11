"""Custom Grimoire themes registered on app startup."""

from textual.theme import Theme

# Inspired by D&D Beyond's dark UI: their signature crimson red,
# warm near-black backgrounds, and gold legendary accents.
classic_dnd = Theme(
    name="classic-dnd",
    dark=True,
    primary="#C5000E",       # D&D Beyond signature red — primary buttons
    secondary="#8B0000",     # deeper blood red
    accent="#FFB62A",        # D&D Beyond gold (legendary)
    background="#0F1215",    # very dark warm-cool black
    surface="#1A2028",       # dark slate surface
    panel="#242F3A",         # slightly lighter panel — default buttons
    warning="#ED6C02",       # orange warning — warning buttons
    error="#8B1A00",         # dark burnt red — error buttons (distinct from primary)
    success="#4CAF50",       # green success
)

# Inspired by 5e.tools: near-black background, muted steel blue
# for interactive elements — functional and dense reference-tool feel.
five_etools = Theme(
    name="5e-tools",
    dark=True,
    primary="#5B8FC9",       # steel blue — primary buttons
    secondary="#3A6B99",     # deeper blue
    accent="#7EB3E8",        # light blue highlight
    background="#0A0A0C",    # near-black with faint blue tint
    surface="#131318",       # dark surface
    panel="#1C1C24",         # slightly lighter panel — default buttons
    warning="#D4A017",       # amber — warning buttons
    error="#8B2020",         # dark muted red — error buttons
    success="#3D9970",       # muted green
)

# Arcane: deep violet-black, amethyst primary, lavender highlights —
# evokes magic, spell lists, the ethereal plane.
arcane = Theme(
    name="arcane",
    dark=True,
    primary="#9B59B6",       # amethyst purple — primary buttons
    secondary="#6C3483",     # deep violet
    accent="#E8A0F0",        # soft lavender highlight
    background="#0B0813",    # darkest purple-black
    surface="#130E1E",       # dark purple surface
    panel="#1A1228",         # slightly lighter panel — default buttons
    warning="#E6A817",       # golden amber — warning buttons
    error="#7A1A3A",         # dark crimson-rose — error buttons
    success="#27AE60",       # emerald green
)

# Parchment: a warm light theme that evokes old D&D sourcebooks —
# cream pages, brown ink, deep-red chapter headings.
parchment = Theme(
    name="parchment",
    dark=False,
    primary="#7A3500",       # dark oak brown — primary buttons (readable on parchment)
    secondary="#8B4513",     # saddle brown
    accent="#9B1C1C",        # deep red ink accent
    background="#F2E4C4",    # aged parchment
    surface="#E8D5A3",       # slightly darker parchment
    panel="#C4A87A",         # warm tan — default buttons
    warning="#7A5A00",       # dark goldenrod — warning buttons
    error="#8B0000",         # dark red — error buttons
    success="#2D6A4F",       # dark forest green
)

# Gelatinous Cube: dark dungeon black-green, translucent acid-green frame —
# the ooze that silently digests everything it touches.
gelatinous_cube = Theme(
    name="gelatinous-cube",
    dark=True,
    primary="#3d7a57",       # deeper dungeon green — primary buttons
    secondary="#5fa777",     # the cube itself — muted teal-green
    accent="#5fa777",        # frame/border matches the cube
    background="#08100b",    # near-black dungeon floor with green undertone
    surface="#0e1a13",       # dark slimy surface
    panel="#152218",         # slightly lighter — the cube's walls, default buttons
    warning="#b8a030",       # murky gold — warning buttons
    error="#5A2020",         # muted dissolved-red — error buttons
    success="#7dd4a0",       # acid-bright mint — successful digestion
)

GRIMOIRE_THEMES: list = [classic_dnd, five_etools, arcane, parchment, gelatinous_cube]

# Per-theme label colors used in detail views (stat/field labels like "Casting Time:")
THEME_LABEL_COLORS: dict = {
    "classic-dnd": "#FFB62A",  # D&D Beyond gold — warm, legendary
    "5e-tools":    "#5B8FC9",  # deep steel blue (theme primary)
    "arcane":      "#E8A0F0",  # soft lavender (theme accent)
    "parchment":        "#9B1C1C",  # deep red ink — matches the sourcebook accent
    "gelatinous-cube":  "#7dd4a0",  # acid-bright mint — glows against the dark
}

# Per-theme section header colors (e.g. "Actions", "Traits" in monster stat blocks)
THEME_SECTION_COLORS: dict = {
    "classic-dnd": "#C5000E",  # D&D Beyond crimson — chapter/section headings
    "5e-tools":    "#5B8FC9",  # primary steel blue
    "arcane":      "#9B59B6",  # amethyst — distinct from the lighter label color
    "parchment":        "#5C2D0A",  # dark oak brown — ink on parchment
    "gelatinous-cube":  "#5fa777",  # the cube's own green for section headers
}

_DEFAULT_LABEL_COLOR = "#5f87ff"    # original blue for all Textual built-in themes
_DEFAULT_SECTION_COLOR = "yellow"   # original yellow for all Textual built-in themes
