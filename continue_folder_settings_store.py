"""Settings Store Module.

This module provides the SettingsStore class for managing application settings
stored as XML.
"""

import os
import xml.etree.ElementTree as Etree
from collections.abc import Iterable
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
        >>> store = SettingsStore('/path/to/settings.xml', 'Script Title', '1.0.0', attrs)
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

    def __init__(
        self,
        file: str,
        title: str,
        version: str,
        preset_attributes: Iterable[str],
    ) -> None:
        """Initialize the instance.

        Args:
            file: Filepath of existing or to be created XML file of settings.
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
        self.root = None
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

        After loading or creating the tree, initializes the root element and
        presets container element.
        """
        if os.path.isfile(self.file):
            try:
                self.tree = Etree.parse(self.file)
            except (Etree.ParseError, OSError) as error:
                print(f'Error parsing settings file: {error}. Creating new file.')
                self._init_tree()
        else:
            self._init_tree()

        self._get_settings_root()
        self._get_settings_presets()

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

    def _get_settings_root(self) -> None:
        """Store the root element of the XML tree.

        Retrieves and stores the root element ('settings') from the
        ElementTree.
        """
        self.root = self.tree.getroot()

    def _get_presets_path(self) -> str:
        """Get the XPath to the presets element."""
        return (
            f'{self.ELEMENT_SCRIPT_NAME}/'
            f'{self.ELEMENT_VERSION}/'
            f'{self.ELEMENT_PRESETS}'
        )

    def _get_presets_element(self) -> Etree.Element | None:
        """Get the presets container element from the XML tree.

        Returns:
            The presets element, or None if the XML structure is invalid.
        """
        return self.root.find(self._get_presets_path())

    def _get_settings_presets(self) -> None:
        """Store the presets container element from the XML tree.

        Locates and stores the presets container element. If the element cannot
        be found (invalid XML structure), rebuilds the entire tree structure
        and then locates the presets element again.
        """
        self._presets = self._get_presets_element()
        if self._presets is None:
            # Rebuild tree if structure is invalid
            self._init_tree()
            self._get_settings_root()
            self._presets = self._get_presets_element()

    def get_presets(self) -> list[Etree.Element]:
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
        for preset in self.get_presets():
            if preset.get('name') == name:
                return preset
        return None

    def delete(self, *ignore: Any, name: str) -> None:
        """Delete a preset element from the XML tree by name.

        Args:
            *ignore: Additional positional arguments are not allowed.
            name: The name of the preset to delete.

        Raises:
            ValueError: If additional positional arguments are provided, or if
                a preset with the given name does not exist.

        Note:
            Changes are not persisted to disk until save() is called.
        """
        if ignore:
            raise ValueError(
                'SettingsStore.delete() only accepts "name" keyword argument.')
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

    def _check_attributes(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Validate preset kwargs.

        Args:
            kwargs: Preset attribute names and values.

        Raises:
            ValueError: If 'name' is missing or empty, if any preset attribute
                is missing from kwargs, or if kwargs contains keys not in
                preset_attributes.
        """
        if 'name' not in kwargs or not kwargs['name']:
            raise ValueError(
                "Preset must have a non-empty 'name' attribute"
            )
        required = set(self._preset_attributes)
        kwargs_keys = set(kwargs.keys())
        if kwargs_keys < required:
            missing = required - kwargs_keys
            raise ValueError(
                f'Preset is missing required attributes: {sorted(missing)}'
            )
        if kwargs_keys > required:
            extra = kwargs_keys - required
            raise ValueError(
                f'Preset has unexpected attributes: {sorted(extra)}'
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
            ValueError: If kwargs fail _check_attributes validation.

        Note:
            If a preset with the given name doesn't exist, this method
            silently does nothing (no error is raised).
        """
        self._check_attributes(kwargs)
        name_value = kwargs['name']
        preset = self.find_preset(name_value)
        if preset is not None:
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
            dirpath = os.path.dirname(self.file)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
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
            for preset in self.get_presets()
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
        for preset_element in self._presets:
            preset_name = preset_element.get('name', '')
            if preset_name:
                preset = Preset(name=preset_name)
                preset.element = preset_element
                # Legacy XML may use pattern attribute/child instead of
                # input_pattern
                if (
                        not getattr(preset, 'input_pattern', None)
                        and 'input_pattern' in self._preset_attributes
                ):
                    pattern_el = preset_element.find('pattern')
                    legacy_pattern = (
                        pattern_el.text if pattern_el is not None
                        and pattern_el.text is not None
                        else preset_element.get('pattern', '')
                    )
                    if legacy_pattern:
                        preset.input_pattern = legacy_pattern
                if (
                        not getattr(preset, 'output_pattern', None)
                        and 'output_pattern' in self._preset_attributes
                ):
                    preset.output_pattern = '[version]'
                results[preset.name] = preset
        return results
