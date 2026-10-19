"""Preset Module.

This module provides the Preset class for representing preset configuration
objects with XML serialization support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from xml.etree.ElementTree import Element

from continue_folder_destination import Destination

DEFAULT_INPUT_PATTERN = '{version}'
DEFAULT_OUTPUT_PATTERN = '[version]'


@dataclass(kw_only=True)
class Preset:
    """A named pattern and destination configuration.

    Attributes:
        name: Unique preset identifier.
        input_pattern: Curly-brace pattern used to scan existing folders.
        output_pattern: Square-bracket pattern used to form the new name.
        destinations: Where the new name is created.
    """

    name: str
    input_pattern: str = DEFAULT_INPUT_PATTERN
    output_pattern: str = DEFAULT_OUTPUT_PATTERN
    destinations: set[Destination] = field(
        default_factory=Destination.default,
    )

    @classmethod
    def from_element(cls, element: Element) -> Preset:
        """Build a preset from an XML preset element.

        Missing or empty pattern and destination attributes fall back to
        the same defaults as a newly constructed Preset.
        """
        attrib = element.attrib
        return cls(
            name=attrib.get('name', ''),
            input_pattern=attrib.get('input_pattern') or DEFAULT_INPUT_PATTERN,
            output_pattern=(
                attrib.get('output_pattern') or DEFAULT_OUTPUT_PATTERN),
            destinations=(
                Destination.decode(attrib.get('destinations', ''))
                or Destination.default()
            ),
        )

    def to_element(self) -> Element:
        """Return a new XML preset element for this preset."""
        return Element('preset', attrib={
            'name': self.name,
            'input_pattern': self.input_pattern,
            'output_pattern': self.output_pattern,
            'destinations': Destination.encode(self.destinations),
        })
