"""
Script Name: Continue Folder
Written By: Kieran Hanrahan

Script Version: 3.0.0
Flame Version: 2025

URL: http://www.github.com/khanrahan/continue-folder

Creation Date: 04.10.23
Update Date: 03.06.25

Description:

    Create a new reel on the Desktop and/or folder in the MediaHub Files tab
    using tokens, including a token to continue a number sequence in a sequence
    of existing folders.

Menus:

    Right-click selected folders in the Media Hub --> Create... --> Continue
    Folder

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""


import datetime as dt
import os

import flame
from PySide6 import QtWidgets

from continue_folder_flame_message_window import FlameMessageWindow
from continue_folder_main_window import MainWindow
from continue_folder_save_preset_window import SavePresetWindow
from continue_folder_settings_store import SettingsStore
from continue_folder_token_store_input import InputTokenStore
from continue_folder_token_store_output import OutputTokenStore

TITLE = 'Continue Folder'
VERSION_INFO = (3, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'

CONFIG_FOLDER = '~/.config/continue-folder'
XML = 'continue_folder.xml'


class ContinueFolder:
    """Creates a new folder on the Desktop or in the Media Hub using tokens.

    Input Pattern uses curly-brace tokens (``{version}``, ``{YYYY}``, …) to
    interpret existing destination folders. Output Pattern uses square-bracket
    tokens (``[version]``, ``[YYYY]``, …) to form the new folder name.
    ``{version}`` continues a number sequence; optional hashes set padding
    on input (``{version###}``) or output (``[version###]``).
    """

    def __init__(self, selection):
        """Initialize ContinueFolder and set up the GUI.

        Args:
            selection: Tuple of selected Flame objects provided by the Flame
            API.
        """
        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        self.path = selection[0].path

        # Settings store (presets XML)
        self._settings_file = os.path.join(
            os.path.expanduser(CONFIG_FOLDER), XML)
        self._store = SettingsStore(
            self._settings_file, TITLE, VERSION,
            preset_attributes=(
                'name', 'input_pattern', 'output_pattern', 'destinations')
            )
        self.message(f'Settings loaded from {self._settings_file}')

        # Token stores
        self.now = dt.datetime.now()
        self.input_token_store = InputTokenStore(self.path)
        self.output_token_store = OutputTokenStore(
            epoch=self.now,
            input_token_store=self.input_token_store,
        )

        # Patterns, folders, destinations — filled by apply_preset
        self.input_pattern = '{version}'
        self.output_pattern = '[version]'
        self.folders = []
        self.pattern_regex = ''
        self.folder_new = ''
        self.destinations = {'Desktop Reel': True, 'Media Hub': False}

        # Windows
        self._windows = {
            'parent': self._get_flame_parent(),
            'main': None,
            'save': None,
        }
        self._windows['main'] = MainWindow(
            TITLE_VERSION, self._windows['parent'])
        self._windows['save'] = SavePresetWindow(self._windows['main'])

        self._windows['main'].presets = self._store.preset_names
        self._windows['main'].input_tokens = (
            self.input_token_store.name_token_pairs)
        self._windows['main'].output_tokens = (
            self.output_token_store.name_token_pairs)

        # Window signals
        self._windows['main'].signal_preset.connect(self._on_preset_change)
        self._windows['main'].signal_save.connect(self._on_preset_save)
        self._windows['main'].signal_delete.connect(self._on_preset_delete)
        self._windows['main'].signal_input_pattern.connect(
            self._on_input_pattern_change)
        self._windows['main'].signal_output_pattern.connect(
            self._on_output_pattern_change)
        self._windows['main'].signal_destination.connect(
            self._on_destinatination_change)
        self._windows['main'].signal_ok.connect(self._on_ok_clicked)
        self._windows['main'].signal_cancel.connect(self._on_cancel_clicked)

        preset_zero = (
            self._store.preset_names[0] if self._store.preset_names else None)
        self.apply_preset(preset_zero)

        self._windows['main'].show()

    @staticmethod
    def message(string):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        print(' '.join([MESSAGE_PREFIX, string]))

    @staticmethod
    def _get_flame_parent():
        """Return Flame main window as parent for dialogs, or None."""
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.objectName() == 'CF Main Window':
                return widget
        return None

    @staticmethod
    def _patterns_from_preset(preset) -> tuple[str, str]:
        """Read input/output patterns from a preset, with legacy fallback."""
        input_pattern = (
            getattr(preset, 'input_pattern', None)
            or getattr(preset, 'pattern', None)
            or '{version}')
        output_pattern = getattr(preset, 'output_pattern', None) or '[version]'
        return input_pattern, output_pattern

    def _apply_patterns(self) -> None:
        """Scan with input pattern and resolve the output pattern."""
        self.input_token_store.apply(self.input_pattern)
        self.folders = self.input_token_store.folders
        self.pattern_regex = self.input_token_store.pattern_regex
        self.folder_new = self.output_token_store.resolve(self.output_pattern)

    def _refresh_folder_display(self):
        """Recompute folder name from patterns and update window display."""
        self._apply_patterns()
        self._windows['main'].folder_new = self.folder_new

    def _on_destinatination_change(self):
        """Update destinations dictionary from window checkboxes."""
        self.destinations['Desktop Reel'] = (
            self._windows['main'].destination_reel_checked
        )
        self.destinations['Media Hub'] = (
            self._windows['main'].destination_folder_checked
        )

    def apply_preset(self, name: str | None) -> None:
        """Load a preset into the model and push it to the main window.

        Missing or unknown names fall back to default patterns and
        destinations. Call this after the window exists, including on
        startup (setText does not emit ``signal_preset``).
        """
        preset = self._store.presets.get(name) if name else None
        if preset:
            self.input_pattern, self.output_pattern = (
                self._patterns_from_preset(preset))
            self._load_destinations(preset)
        else:
            self.input_pattern = '{version}'
            self.output_pattern = '[version]'
            self.destinations = {'Desktop Reel': True, 'Media Hub': False}

        main = self._windows['main']
        main.preset = name or ''
        main.input_pattern = self.input_pattern
        main.output_pattern = self.output_pattern
        main.destination_reel_checked = self.destinations.get(
            'Desktop Reel', False)
        main.destination_folder_checked = self.destinations.get(
            'Media Hub', False)
        self._refresh_folder_display()

    def _on_preset_change(self):
        """Handle preset selection change; reload from the store."""
        self.apply_preset(self._windows['main'].preset)

    def _on_input_pattern_change(self, text):
        """Handle input pattern change; update folder and update display."""
        self.input_pattern = text
        self._refresh_folder_display()

    def _on_output_pattern_change(self, text):
        """Handle output pattern change; update folder and update display."""
        self.output_pattern = text
        self._refresh_folder_display()

    def _on_preset_delete(self):
        """Handle preset delete button; confirm then delete and reload."""
        preset_name = self._windows['main'].preset
        if not FlameMessageWindow(
                'Confirm Operation', 'confirm', 'Are you sure want to'
                + ' permanently delete this preset?' + '<br/>' + 'This operation'
                + ' cannot be undone.'):
            return
        try:
            self._store.delete(name=preset_name)
            self._store.save()
            self.message(
                f'{preset_name} preset deleted from {self._settings_file}')
        except ValueError:
            pass
        self._store.load()
        self._windows['main'].presets = self._store.preset_names
        next_preset = (
            self._store.preset_names[0] if self._store.preset_names else None)
        self.apply_preset(next_preset)

    def _encode_destinations(self):
        """Encode destinations dict as a comma separated string."""
        return ', '.join(
            key for key, value in self.destinations.items() if value is True
        )

    def _on_preset_save(self):
        """Show save preset dialog and save or overwrite preset on accept."""
        self._windows['save'].name = self._windows['main'].preset
        if self._windows['save'].exec_() != QtWidgets.QDialog.Accepted:
            return
        preset_name = self._windows['save'].name
        duplicate = self._store.find_preset(preset_name) is not None
        if duplicate:
            if not FlameMessageWindow(
                    'Overwrite Existing Preset', 'confirm', 'Are you '
                    + 'sure want to permanently overwrite this preset?'
                    + '<br/>' + 'This operation cannot be undone.'):
                return
            self._store.overwrite_preset(
                name=preset_name,
                input_pattern=self.input_pattern,
                output_pattern=self.output_pattern,
                destinations=self._encode_destinations()
            )
        else:
            self._store.add_preset(
                name=preset_name,
                input_pattern=self.input_pattern,
                output_pattern=self.output_pattern,
                destinations=self._encode_destinations()
            )
            self._store.sort()
        try:
            self._store.save()
            self.message(
                f'{preset_name} preset saved to {self._settings_file}')
        except OSError:
            FlameMessageWindow(
                'Error', 'error',
                f'Check permissions on {self._settings_file}')
            return
        self._windows['main'].presets = self._store.preset_names
        self.apply_preset(preset_name)

    def _on_ok_clicked(self):
        """Handle OK button; create reel or folder then close."""
        if self._windows['main'].destination_reel_checked:
            self.create_desktop_reel()
        if self._windows['main'].destination_folder_checked:
            self.create_media_hub_folder()
        self.message('Done!')
        self._windows['main'].close()

    def _on_cancel_clicked(self):
        """Handle Cancel button."""
        self.message('Cancelled!')
        self._windows['main'].close()

    def _load_destinations(self, preset):
        """Load destinations from preset."""
        destinations = getattr(preset, 'destinations', None)
        if destinations:
            loaded_destinations = destinations.split(', ')
            for destination in self.destinations:
                if destination in loaded_destinations:
                    self.destinations[destination] = True
                else:
                    self.destinations[destination] = False
        else:
            self.destinations = {'Desktop Reel': True, 'Media Hub': False}

    def create_desktop_reel(self):
        """Create reel on bottom of the current desktop.

        This will start a folder sequence or continue an existing folder
        sequence.
        """
        desktop = flame.project.current_project.current_workspace.desktop
        # create_real will not take utf-8, only ascii
        desktop.reel_groups[0].create_reel(self.folder_new.encode('ascii', 'ignore'))
        self.message('Reel created!')

    def create_media_hub_folder(self):
        """Create folder in Media Hub.

        This will start a folder sequence or continue the existing folder
        sequence.
        """
        os.mkdir(os.path.join(self.path, self.folder_new))
        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")
        self.message('MediaHub folder created!')


def scope_folder(selection):
    """Determine if selection is a one folder in the MediaHub > Files tab."""
    return len(selection) == 1 and isinstance(selection[0], flame.PyMediaHubFilesFolder)


def get_mediahub_files_custom_ui_actions():
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
