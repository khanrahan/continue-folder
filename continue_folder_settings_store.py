"""Settings Store Module.

This module provides the SettingsStore class for managing application settings
stored as XML.
"""

import xml.etree.ElementTree as Etree
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from continue_folder_preset import Preset


class SettingsStore:
    """Manages application settings stored as XML.

    This class provides a high-level interface for reading, writing, and
    managing preset configurations stored in an XML file. It handles XML
    parsing, validation, and provides methods to add, delete, update, and query
    presets.

    The XML structure follows this hierarchy:

    .. code-block:: xml

        <settings>
            <script_name>Script Name
                <version>X.X.X
                    <presets>
                        <preset name="preset_name" path="..." pattern="..." find="...">
                        </preset>
                    </presets>
                </version>
            </script_name>
        </settings>

    Preset attribute names are passed in at initialization via preset_attributes.
    The 'name' attribute must always be present in preset_attributes (it is the
    required unique identifier).

    Example:
        >>> attrs = ('name', 'path', 'pattern', 'find')
        >>> store = SettingsStore(Path('/path/to/settings.xml'), 'Script Title', '1.0.0', attrs)
        >>> store.add_preset(name='My Preset', path='/some/path', pattern='<DD>')
        >>> store.save()
        >>> presets = store.preset_names
        >>> store.delete(name='My Preset')
    """  # noqa: W505

    # XML tree element names
    ELEMENT_ROOT = 'settings'
    ELEMENT_SCRIPT_NAME = 'script_name'
    ELEMENT_VERSION = 'version'
    ELEMENT_PRESETS = 'presets'
    ELEMENT_PRESET = 'preset'
    PRESETS_PATH = f'{ELEMENT_SCRIPT_NAME}/{ELEMENT_VERSION}/{ELEMENT_PRESETS}'

    def __init__(
        self,
        file: Path,
        title: str,
        version: str,
        preset_attributes: Iterable[str],
    ) -> None:
        """Initialize the instance.

        Args:
            file: Path of an existing or to-be-created XML settings file.
            title: Script title for the XML structure.
            version: Script version for the XML structure.
            preset_attributes: Iterable of preset XML attribute names. Must
                include 'name' (the required unique identifier). Defines which
                attributes presets may have.

        Raises:
            ValueError: If 'name' is not in preset_attributes.
        """
        self._preset_attributes = tuple(preset_attributes)
        self._check_name_attribute()
        self.file = file
        self.title = title
        self.version = version
        self.tree = None
        self._presets = None
        self.load()

    def _check_name_attribute(self) -> None:
        """Ensure preset_attributes includes the required 'name' attribute.

        Raises:
            ValueError: If 'name' is not in preset_attributes.
        """
        if 'name' not in self._preset_attributes:
            raise ValueError(
                "'name' must always be present in preset_attributes"
            )

    def load(self) -> None:
        """Load settings from XML file and initialize the XML tree.

        If the file exists, attempts to parse it. If parsing fails (corrupted
        or malformed XML), creates a new empty XML tree structure. If the file
        doesn't exist, creates a new empty XML tree structure.

        After loading or creating the tree, initializes the presets container
        element.
        """
        if self.file.is_file():
            try:
                self.tree = Etree.parse(self.file)
            except (Etree.ParseError, OSError) as error:
                print(f'Error parsing settings file: {error}. Creating new file.')
                self._init_tree()
        else:
            self._init_tree()

        self._load_presets_element()

    def _init_tree(self) -> None:
        """Create a new empty XML tree with the required structure.

        See class docstring for XML structure.
        """
        settings = Etree.Element(self.ELEMENT_ROOT)

        name = Etree.SubElement(settings, self.ELEMENT_SCRIPT_NAME)
        name.text = self.title

        version = Etree.SubElement(name, self.ELEMENT_VERSION)
        version.text = self.version

        _presets = Etree.SubElement(version, self.ELEMENT_PRESETS)
        self.tree = Etree.ElementTree(settings)

    def _load_presets_element(self) -> None:
        """Store the presets container element from the XML tree.

        Locates and stores the presets container element. If the element cannot
        be found (invalid XML structure), rebuilds the entire tree structure
        and then locates the presets element again.
        """
        self._presets = self.tree.find(self.PRESETS_PATH)
        if self._presets is None:
            # Rebuild tree if structure is invalid
            self._init_tree()
            self._presets = self.tree.find(self.PRESETS_PATH)

    def _get_preset_elements(self) -> list[Etree.Element]:
        """Return a list of preset Element objects.

        Returns:
            List of ElementTree Element objects representing presets.
            Returns empty list if no presets exist or XML structure is invalid.

        Note:
            The returned elements are mutable references to the XML tree.
            Modifications to these elements will affect the underlying tree.
        """
        return self._presets.findall(self.ELEMENT_PRESET)

    def find_preset(self, name: str) -> Etree.Element | None:
        """Find a preset element by name.

        Args:
            name: The preset name to search for.

        Returns:
            The preset element if found, None otherwise.
        """
        for preset in self._get_preset_elements():
            if preset.get('name') == name:
                return preset
        return None

    def delete(self, *, name: str) -> None:
        """Delete a preset element from the XML tree by name.

        Args:
            name: The name of the preset to delete.

        Raises:
            ValueError: If a preset with the given name does not exist.

        Note:
            Changes are not persisted to disk until save() is called.
        """
        preset = self.find_preset(name)
        if preset is None:
            raise ValueError(f'Preset "{name}" does not exist.')
        self._presets.remove(preset)

    def sort(self) -> None:
        """Alphabetically sort presets by name attribute.

        Sorts all preset elements in-place based on their 'name' attribute.
        The sorting is case-sensitive and uses the default string comparison.
        Presets without a name attribute are sorted as empty strings.

        Note:
            This modifies the XML tree structure directly. Changes are not
            persisted to disk until save() is called.
        """
        self._presets[:] = sorted(
            self._presets,
            key=lambda preset: preset.get('name', '')
        )

    def _check_attributes(self, kwargs: dict[str, Any]) -> None:
        """Validate preset kwargs.

        Args:
            kwargs: Preset attribute names and values.

        Raises:
            ValueError: If 'name' is missing or empty, or if kwargs keys do
                not exactly match preset_attributes.
        """
        if not kwargs.get('name'):
            raise ValueError("Preset must have a non-empty 'name' attribute")
        if kwargs.keys() != set(self._preset_attributes):
            raise ValueError(
                f'Preset attributes must be exactly '
                f'{sorted(self._preset_attributes)}, got {sorted(kwargs)}'
            )

    def add_preset(self, **kwargs: Any) -> None:
        """Add preset Element object to the presets Element Tree.

        Args:
            **kwargs: Preset attributes. Must include 'name' with a non-empty
                value. Only attributes in preset_attributes are stored.

        Raises:
            ValueError: If 'name' attribute is missing or empty.
        """
        self._check_attributes(kwargs)
        preset = Preset(**kwargs)
        self._presets.append(preset.element)

    def overwrite_preset(self, **kwargs: Any) -> None:
        """Update attributes of an existing preset in the XML tree.

        The 'name' value is used to locate the preset. Kwargs must match
        preset_attributes exactly (same validation as add_preset).

        Args:
            **kwargs: Full set of preset attributes. Must include 'name' and
                all other preset_attributes.

        Raises:
            ValueError: If kwargs fail _check_attributes validation, or if a
                preset with the given name does not exist.
        """
        self._check_attributes(kwargs)
        name_value = kwargs['name']
        preset = self.find_preset(name_value)
        if preset is None:
            raise ValueError(f'Preset "{name_value}" does not exist.')
        for key, value in kwargs.items():
            preset.set(key, value)

    def save(self) -> None:
        """Write the XML tree to the settings file.

        Creates the directory path if it doesn't exist, then writes the
        current XML tree structure to the file specified during initialization.

        Raises:
            OSError: If the file cannot be written (e.g., permission denied,
                disk full, or invalid path).
        """
        try:
            self.file.parent.mkdir(parents=True, exist_ok=True)
            self.tree.write(self.file)
        except OSError as error:
            raise OSError(f'Failed to save settings to {self.file}: {error}') from error

    @property
    def preset_names(self) -> list[str]:
        """Return a list of all preset names.

        Returns:
            List of preset name strings.  Returns empty list if no valid
            presets exist.
        """
        return [
            preset.get('name', '')
            for preset in self._get_preset_elements()
            if preset.get('name')
        ]

    @property
    def presets(self) -> dict[str, Preset]:
        """Return a dictionary of Preset objects keyed by preset name.

        Returns:
            Dictionary mapping preset names to Preset objects. Each Preset
            object wraps an ElementTree Element and provides convenient
            attribute access.
        """
        results = {}
        for preset_element in self._get_preset_elements():
            preset_name = preset_element.get('name', '')
            if preset_name:
                preset = Preset(name=preset_name)
                preset.element = preset_element
                results[preset.name] = preset
        return results
