"""Preset Module.

This module provides the Preset class for representing preset configuration
objects with XML serialization support.
"""

import xml.etree.ElementTree as Etree
from typing import Any


class Preset:
    """An single Preset object.

    The Element Tree element would appear as below:
    <preset name="preset name"></preset>
    """

    def __init__(self, *, name: str, **kwargs: Any) -> None:
        """Initialize the object.

        Args:
            name: Name of the preset. Must be a non-empty string.
            **kwargs: Additional preset attributes to store.

        Raises:
            TypeError: If name is not a string.
            ValueError: If name is empty.
        """
        if not isinstance(name, str):
            raise TypeError(
                f'name must be a string, got {type(name).__name__}')
        if not name:
            raise ValueError('name cannot be empty')
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def element(self) -> Etree.Element:
        """Add preset Element object to the presets Element Tree."""
        preset = Etree.Element(
            'preset',
            attrib=self.__dict__,
        )
        return preset

    @element.setter
    def element(self, element: Etree.Element) -> None:
        for attribute, value in element.attrib.items():
            setattr(self, attribute, value)
