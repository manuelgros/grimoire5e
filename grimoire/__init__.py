"""Grimoire 5e — D&D 5th Edition reference TUI."""

from importlib.metadata import PackageNotFoundError, version as _version

try:
    __version__ = _version("grimoire5e")
except PackageNotFoundError:
    # Running from a source checkout that was never installed.
    __version__ = "0.3.0"
