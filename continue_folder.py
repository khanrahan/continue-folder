"""
Script Name: Continue Folder
Written By: Kieran Hanrahan

Script Version: 4.0.2
Flame Version: 2025

URL: http://www.github.com/khanrahan/continue-folder

Creation Date: 04.10.23
Update Date: 10.20.26

Description:

    Create a new reel on the Desktop and/or folder in the MediaHub Files tab
    using tokens, including a token to continue a number sequence in a sequence
    of existing folders.

Menus:

    Right-click a selected folder in MediaHub Files --> Create... -->
    Continue Folder

To Install:

    Copy all of the continue_folder*.py files together into the same folder.

    For all users, copy the files to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy the files to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy the files to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""  # noqa: D205, D212, D415


import unicodedata
from pathlib import Path

import flame
from PySide6 import QtWidgets

from continue_folder_destination import Destination
from continue_folder_preset import Preset
from continue_folder_pyflame_message_window import PyFlameMessageWindow
from continue_folder_settings_store import SettingsStore
from continue_folder_token_store_input import TokenStoreInput
from continue_folder_token_store_output import TokenStoreOutput
from continue_folder_window_main import WindowMain
from continue_folder_window_save_preset import WindowSavePreset

TITLE = 'Continue Folder'
VERSION_INFO = (4, 0, 2)
VERSION = '.'.join(map(str, VERSION_INFO))
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'

CONFIG_FOLDER = '~/.config/continue-folder'
XML = 'continue_folder.xml'


class ContinueFolder:
    """Creates a new Desktop reel or MediaHub Folder using tokens.

    Input Pattern uses curly-brace tokens ({version}, {YYYY}, …) to
    interpret existing destination folders. Output Pattern uses square-bracket
    tokens ([version], [YYYY], …) to form the new folder name.
    {version} continues a number sequence; optional hashes set padding
    on output ([version###]).
    """

    def __init__(self, selection: tuple) -> None:
        """Initialize ContinueFolder and set up the GUI.

        Args:
            selection: Tuple of selected Flame objects provided by the Flame
            API.
        """
        self._message(TITLE_VERSION)
        self._message(f'Script called from {__file__}')

        self.path = selection[0].path

        # Settings store (presets XML)
        self._settings_file = Path(CONFIG_FOLDER).expanduser() / XML
        self._store = SettingsStore(self._settings_file, TITLE, VERSION)
        self._message(f'Settings loaded from {self._settings_file}')

        # Token stores
        self.token_store_input = TokenStoreInput(self.path)
        self.token_store_output = TokenStoreOutput(
            token_store_input=self.token_store_input,
        )

        # Windows
        self._windows = {
            'parent': self._get_flame_parent(),
            'main': None,
            'save': None,
        }
        self._windows['main'] = WindowMain(
            TITLE_VERSION, self._windows['parent'])
        self._windows['save'] = WindowSavePreset(self._windows['main'])

        self._windows['main'].presets = self._store.preset_names
        self._windows['main'].input_tokens = (
            self.token_store_input.name_token_pairs)
        self._windows['main'].output_tokens = (
            self.token_store_output.name_token_pairs)

        # Window signals
        self._windows['main'].signal_preset.connect(self._on_preset_change)
        self._windows['main'].signal_save.connect(self._on_preset_save)
        self._windows['main'].signal_delete.connect(self._on_preset_delete)
        self._windows['main'].signal_input_pattern.connect(
            self._on_pattern_change)
        self._windows['main'].signal_output_pattern.connect(
            self._on_pattern_change)
        self._windows['main'].signal_ok.connect(self._on_ok_clicked)
        self._windows['main'].signal_cancel.connect(self._on_cancel_clicked)

        self.apply_preset(self._preset_name_zero())

        self._windows['main'].show()

    @staticmethod
    def _message(text: str) -> None:
        """Print message to shell window and prepend global MESSAGE_PREFIX."""
        print(MESSAGE_PREFIX, text)

    @staticmethod
    def _get_flame_parent() -> QtWidgets.QWidget | None:
        """Return Flame main window as parent for dialogs, or None."""
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.objectName() == 'CF Main Window':
                return widget
        return None

    @staticmethod
    def _convert_to_ascii(text: str) -> str:
        """Convert a unicode string to ASCII, ignoring non-ASCII characters.

        All strings in Python3 are unicode, but Flame only accepts ASCII.
        """
        if text.isascii():
            return text
        # NFKD normalization splits accented letters into a letter and
        # separate accent
        normalized = unicodedata.normalize('NFKD', text)
        # ASCII bytes will ignore the accents, emoji, and other non-ASCII
        # characters
        ascii_bytes = normalized.encode('ascii', 'ignore')
        # finally decode to ASCII string
        ascii_string = ascii_bytes.decode('ascii')
        return ascii_string

    def _refresh_folder_display(self) -> None:
        """Recompute folder name from patterns and update window display.

        Because Flame only accepts ASCII, convert before showing, which may
        differ from output pattern.
        """
        main = self._windows['main']
        self.token_store_input.apply(main.input_pattern)
        result = self.token_store_output.resolve(main.output_pattern)
        main.folder_new = self._convert_to_ascii(result)

    def _preset_name_zero(self) -> str | None:
        """Return the first preset name, or None if no presets exist."""
        return self._store.preset_names[0] if self._store.preset_names else None

    def apply_preset(self, name: str | None) -> None:
        """Load a preset into the model and push it to the main window.

        Missing or unknown names fall back to default patterns and
        destinations. Call this after the window exists, including on
        startup (setText does not emit signal_preset).
        """
        preset = self._store.presets.get(name) if name else None
        if preset is None:
            preset = Preset(name=name or '')
        main = self._windows['main']
        main.input_pattern = preset.input_pattern
        main.output_pattern = preset.output_pattern
        main.destinations = preset.destinations
        main.preset = preset.name
        self._refresh_folder_display()

    def _on_preset_change(self) -> None:
        """Handle preset selection change; reload from the store."""
        self.apply_preset(self._windows['main'].preset)

    def _on_pattern_change(self, _text: str) -> None:
        """Input or Output pattern change.

        Recompute folder and update display.  Ignore the string emitted by
        PyFlameLineEdit.
        """
        self._refresh_folder_display()

    def _on_preset_delete(self) -> None:
        """Handle preset delete button; confirm then delete and reload."""
        main = self._windows['main']
        preset_name = main.preset
        if not PyFlameMessageWindow.confirm(
                'Confirm Operation',
                'Are you sure you want to permanently delete this preset?<br/>'
                'This operation cannot be undone.',
                main):
            return
        try:
            self._store.delete_preset(name=preset_name)
        except ValueError as error:
            PyFlameMessageWindow.error(str(error), main)
            return
        try:
            self._store.save()
        except OSError:
            PyFlameMessageWindow.error(
                f'Check permissions on {self._settings_file}', main)
            # delete_preset() already removed the preset from memory; reload
            # the file that failed to update.
            self._store.load()
            return
        self._message(
            f'{preset_name} preset deleted from {self._settings_file}')
        self._windows['main'].presets = self._store.preset_names
        self.apply_preset(self._preset_name_zero())

    def _on_preset_save(self) -> None:
        """Show save preset dialog and save or overwrite preset on accept."""
        if not self._windows['main'].destinations:
            PyFlameMessageWindow.error(
                'Select at least one destination before saving a preset.',
                self._windows['main'])
            return
        self._windows['save'].name = self._windows['main'].preset
        if self._windows['save'].exec() != QtWidgets.QDialog.Accepted:
            return
        # Strip leading/trailing whitespace to avoid names of only spaces.
        preset_name = self._windows['save'].name.strip()
        if not preset_name:
            PyFlameMessageWindow.error(
                'Name field cannot be empty.', self._windows['main'])
            return
        duplicate = preset_name in self._store.preset_names
        if duplicate and not PyFlameMessageWindow.confirm(
                'Overwrite Existing Preset',
                'Are you sure you want to permanently overwrite this '
                'preset?<br/>This operation cannot be undone.',
                self._windows['main']):
            return
        preset = Preset(
            name=preset_name,
            input_pattern=self._windows['main'].input_pattern,
            output_pattern=self._windows['main'].output_pattern,
            destinations=self._windows['main'].destinations,
        )
        try:
            if duplicate:
                self._store.overwrite_preset(preset)
            else:
                self._store.add_preset(preset)
                self._store.sort_presets()
        except ValueError as error:
            PyFlameMessageWindow.error(str(error), self._windows['main'])
            return
        try:
            self._store.save()
        except OSError:
            PyFlameMessageWindow.error(
                f'Check permissions on {self._settings_file}',
                self._windows['main'])
            # put in memory & whats on disk back in sync
            self._store.load()
            return
        self._message(f'{preset_name} preset saved to {self._settings_file}')
        self._windows['main'].presets = self._store.preset_names
        self.apply_preset(preset_name)

    def _on_ok_clicked(self) -> None:
        """Handle OK button; create reel or folder then close."""
        if not self._windows['main'].folder_new:
            PyFlameMessageWindow.error(
                'New Folder field is empty.  Check your input and output patterns.',
                self._windows['main'])
            return
        destinations = self._windows['main'].destinations
        if not destinations:
            PyFlameMessageWindow.error(
                'Select at least one destination.', self._windows['main'])
            return
        if Destination.REEL in destinations:
            self.create_desktop_reel()
        if Destination.FOLDER in destinations:
            self.create_media_hub_folder()
        self._message('Done!')
        self._windows['main'].close()

    def _on_cancel_clicked(self) -> None:
        """Handle Cancel button."""
        self._message('Cancelled!')
        self._windows['main'].close()

    def create_desktop_reel(self) -> None:
        """Create reel on bottom of the current desktop.

        This will start a folder sequence or continue an existing folder
        sequence.
        """
        desktop = flame.project.current_project.current_workspace.desktop
        desktop.reel_groups[0].create_reel(self._windows['main'].folder_new)
        self._message('Reel created!')

    def create_media_hub_folder(self) -> None:
        """Create folder in MediaHub Folder.

        This will start a folder sequence or continue the existing folder
        sequence.
        """
        Path(self.path, self._windows['main'].folder_new).mkdir()
        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")
        self._message('MediaHub folder created!')


def scope_folder(selection: tuple) -> bool:
    """Determine if selection is one folder in the MediaHub > Files tab."""
    return len(selection) == 1 and isinstance(selection[0], flame.PyMediaHubFilesFolder)


def get_mediahub_files_custom_ui_actions() -> list[dict]:
    """Add right click menu items."""
    menu_name = 'Create...'
    action = {
        'name': 'Continue Folder',
        'isVisible': scope_folder,
        'execute': ContinueFolder,
        'minimumVersion': '2025.0.0.0'
    }
    menu = {'name': menu_name, 'actions': [action]}
    return [menu]
