"""Destination Module.

This module provides the Destination enum for where the new name is created.
"""

from collections.abc import Set
from enum import StrEnum


class Destination(StrEnum):
    """Where the new folder name is created.

    Values double as button labels and as the text stored in presets.
    """

    REEL = 'Desktop Reel'
    FOLDER = 'MediaHub Folder'

    @classmethod
    def default(cls) -> set['Destination']:
        """Return the destinations used when a preset has none stored."""
        return {cls.REEL}

    @classmethod
    def decode(cls, text: str) -> set['Destination']:
        """Parse comma-separated preset text, ignoring unknown names."""
        names = {name.strip() for name in text.split(',')}
        return {member for member in cls if member in names}

    @classmethod
    def encode(cls, destinations: Set['Destination']) -> str:
        """Join destinations as comma-separated text in definition order."""
        return ', '.join(member for member in cls if member in destinations)
