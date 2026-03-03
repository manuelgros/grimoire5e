"""Custom Grimoire themes registered on app startup."""

from textual.theme import Theme

# Inspired by D&D Beyond's dark UI: their signature crimson red,
# warm near-black backgrounds, and gold legendary accents.
classic_dnd = Theme(
    name="classic-dnd",
    dark=True,
    primary="#C5000E",       # D&D Beyond signature red
    secondary="#8B0000",     # deeper blood red
    accent="#FFB62A",        # D&D Beyond gold (legendary)
    background="#0F1215",    # very dark warm-cool black
    surface="#1A2028",       # dark slate surface
    panel="#242F3A",         # slightly lighter panel
    warning="#ED6C02",       # orange warning
    error="#F44336",         # bright red error
    success="#4CAF50",       # green success
)

# Inspired by 5e.tools: near-black background, muted steel blue
# for interactive elements — functional and dense reference-tool feel.
five_etools = Theme(
    name="5e-tools",
    dark=True,
    primary="#5B8FC9",       # steel blue (link/nav colour)
    secondary="#3A6B99",     # deeper blue
    accent="#7EB3E8",        # light blue highlight
    background="#0A0A0C",    # near-black with faint blue tint
    surface="#131318",       # dark surface
    panel="#1C1C24",         # slightly lighter panel
    warning="#D4A017",       # amber
    error="#C04040",         # muted red
    success="#3D9970",       # muted green
)

# Arcane: deep violet-black, amethyst primary, lavender highlights —
# evokes magic, spell lists, the ethereal plane.
arcane = Theme(
    name="arcane",
    dark=True,
    primary="#9B59B6",       # amethyst purple
    secondary="#6C3483",     # deep violet
    accent="#E8A0F0",        # soft lavender highlight
    background="#0B0813",    # darkest purple-black
    surface="#130E1E",       # dark purple surface
    panel="#1A1228",         # slightly lighter panel
    warning="#E6A817",       # golden amber
    error="#CF3A3A",         # red
    success="#27AE60",       # emerald green
)

# Parchment: a warm light theme that evokes old D&D sourcebooks —
# cream pages, brown ink, deep-red chapter headings.
parchment = Theme(
    name="parchment",
    dark=False,
    primary="#5C2D0A",       # dark oak brown (headings/primary)
    secondary="#8B4513",     # saddle brown
    accent="#9B1C1C",        # deep red ink accent
    background="#F2E4C4",    # aged parchment
    surface="#E8D5A3",       # slightly darker parchment
    panel="#D4BA7A",         # tan panel
    warning="#B8860B",       # dark goldenrod
    error="#8B0000",         # dark red
    success="#2D6A4F",       # dark forest green
)

GRIMOIRE_THEMES: list = [classic_dnd, five_etools, arcane, parchment]
