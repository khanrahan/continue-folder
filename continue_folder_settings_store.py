"""Settings Store Module.

This module provides the SettingsStore class for managing application settings
stored as XML.
"""

import re
import xml.etree.ElementTree as Etree
from pathlib import Path

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
                        <preset name="..." input_pattern="..."
                            output_pattern="..." destinations="...">
                        </preset>
                    </presets>
                </version>
            </script_name>
        </settings>

    Presets are loaded from the <version> element whose major version
    matches the running script. Older major-version blocks are left in the
    file unused. Other children of <version> (for example history) can
    be loaded the same way as presets.

    Example:
        >>> store = SettingsStore(
        ...     Path('/path/to/settings.xml'), 'Title', '1.0.0')
        >>> store.add_preset(Preset(name='My Preset'))
        >>> store.save()
        >>> presets = store.preset_names
        >>> store.delete_preset(name='My Preset')
    """

    # XML tree element names
    ELEMENT_ROOT = 'settings'
    ELEMENT_SCRIPT_NAME = 'script_name'
    ELEMENT_VERSION = 'version'
    ELEMENT_PRESETS = 'presets'
    ELEMENT_PRESET = 'preset'

    def __init__(
        self,
        file: Path,
        title: str,
        version: str,
    ) -> None:
        """Initialize the instance.

        Args:
            file: Path of an existing or to-be-created XML settings file.
            title: Script title for the XML structure.
            version: Script version for the XML structure.
        """
        self.file = file
        self.title = title
        self.version = version
        self.tree = None
        self._version_element = None
        self._presets_element = None
        self.load()

    def load(self) -> None:
        """Load settings from XML file and initialize the XML tree.

        If the file exists, attempts to parse it. If parsing fails (corrupted
        or malformed XML), creates a new empty XML tree structure. If the file
        doesn't exist, creates a new empty XML tree structure.

        After loading or creating the tree, resolves the current major
        version element and then the presets container beneath it.
        """
        if self.file.is_file():
            try:
                self.tree = Etree.parse(self.file)
            except (Etree.ParseError, OSError) as error:
                print(f'Error parsing settings file: {error}. Creating new file.')
                self._init_tree()
        else:
            self._init_tree()

        self._load_version_element()
        self._load_presets_element()

    def _init_tree(self) -> None:
        """Create a new empty XML tree with the settings root and title."""
        settings = Etree.Element(self.ELEMENT_ROOT)

        name = Etree.SubElement(settings, self.ELEMENT_SCRIPT_NAME)
        name.text = self.title
        self.tree = Etree.ElementTree(settings)

    @staticmethod
    def _major(version: str) -> str:
        """Return the major component of a dotted version string."""
        return version.strip().split('.', 1)[0]

    @staticmethod
    def _version_key(version: str) -> tuple[int, ...]:
        """Return a sortable key for a dotted version string.

        Each dotted component contributes its leading integer, so
        '3.10.0' sorts above '3.9.2'. Components without a leading
        number (for example 'beta') count as 0.
        """
        key = []
        for part in version.strip().split('.'):
            match = re.match(r'\d+', part)
            key.append(int(match.group()) if match else 0)
        return tuple(key)

    def _load_version_element(self) -> None:
        """Store the version element for the current major version.

        Finds the highest saved <version> whose major number matches
        self.version (for example, running 3.1.0 with 3.0.0 and
        3.2.0 saved selects 3.2.0). If none exists, appends a new
        empty version element. The selected element's text is then set to
        self.version so the next save records the running version.
        Other major-version blocks are left untouched so later siblings of
        <presets> can share this same element.
        """
        script = self.tree.find(self.ELEMENT_SCRIPT_NAME)
        if script is None:
            self._init_tree()
            script = self.tree.find(self.ELEMENT_SCRIPT_NAME)

        target = self._major(self.version)
        element = max(
            (
                child
                for child in script.findall(self.ELEMENT_VERSION)
                if self._major(child.text or '') == target
            ),
            key=lambda child: self._version_key(child.text or ''),
            default=None,
        )
        if element is None:
            element = Etree.SubElement(script, self.ELEMENT_VERSION)
        element.text = self.version  # Update the current version
        self._version_element = element

    def _load_presets_element(self) -> None:
        """Store the presets container under the current version element.

        Creates an empty <presets> element if the version block does
        not already have one.
        """
        element = self._version_element.find(self.ELEMENT_PRESETS)
        if element is None:
            element = Etree.SubElement(self._version_element, self.ELEMENT_PRESETS)
        self._presets_element = element

    def _get_preset_elements(self) -> list[Etree.Element]:
        """Return a list of preset Element objects.

        Returns:
            List of ElementTree Element objects representing presets.
            Returns empty list if no presets exist or XML structure is invalid.

        Note:
            The returned elements are mutable references to the XML tree.
            Modifications to these elements will affect the underlying tree.
        """
        return self._presets_element.findall(self.ELEMENT_PRESET)

    def _find_preset(self, name: str) -> Etree.Element | None:
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

    def delete_preset(self, *, name: str) -> None:
        """Delete a preset element from the XML tree by name.

        Args:
            name: The name of the preset to delete.

        Raises:
            ValueError: If a preset with the given name does not exist.

        Note:
            Changes are not persisted to disk until save() is called.
        """
        preset = self._find_preset(name)
        if preset is None:
            raise ValueError(f'Preset "{name}" does not exist.')
        self._presets_element.remove(preset)

    def sort_presets(self) -> None:
        """Alphabetically sort presets by name attribute.

        Sorts all preset elements in-place based on their 'name' attribute.
        The sorting is case-sensitive and uses the default string comparison.
        Presets without a name attribute are sorted as empty strings.

        Note:
            This modifies the XML tree structure directly. Changes are not
            persisted to disk until save() is called.
        """
        self._presets_element[:] = sorted(
            self._presets_element,
            key=lambda preset: preset.get('name', '')
        )

    def add_preset(self, preset: Preset) -> None:
        """Add a preset to the XML tree.

        Args:
            preset: The preset to append.

        Raises:
            ValueError: If the preset name is empty.

        Note:
            Changes are not persisted to disk until save() is called.
        """
        if not preset.name:
            raise ValueError("Preset must have a non-empty 'name' attribute")
        self._presets_element.append(preset.to_element())

    def overwrite_preset(self, preset: Preset) -> None:
        """Replace attributes of an existing preset in the XML tree.

        The preset name is used to locate the existing element.

        Args:
            preset: The preset whose attributes replace the stored copy.

        Raises:
            ValueError: If a preset with the given name does not exist.

        Note:
            Changes are not persisted to disk until save() is called.
        """
        element = self._find_preset(preset.name)
        if element is None:
            raise ValueError(f'Preset "{preset.name}" does not exist.')
        element.attrib.clear()
        element.attrib.update(preset.to_element().attrib)

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
            Dictionary mapping preset names to Preset objects.
        """
        return {
            name: Preset.from_element(element)
            for element in self._get_preset_elements()
            if (name := element.get('name'))
        }
