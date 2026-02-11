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
import re

import flame
from PySide6 import QtWidgets

from continue_folder_flame_message_window import FlameMessageWindow
from continue_folder_main_window import MainWindow
from continue_folder_save_preset_window import SavePresetWindow
from continue_folder_settings_store import SettingsStore

TITLE = 'Continue Folder'
VERSION_INFO = (3, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'

CONFIG_FOLDER = '~/.config/continue-folder'
XML = 'continue_folder.xml'


class ContinueFolder:
    """Creates a new folder on the Desktop or in the Media Hub using tokens.

    Currently, the only special token is {version} which will look for a number
    sequence and return the next number in the sequence. All of the other
    tokens are standard things like: day, hour, minute.
    """
    def __init__(self, selection):

        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        self.path = selection[0].path

        # New folder destinations
        self.destinations = [
            'Desktop Reel',
            'Desktop Reel && Media Hub',  # double & to cancel QShortcut
            'Media Hub']

        # Settings store (presets XML)
        self._settings_file = os.path.join(
            os.path.expanduser(CONFIG_FOLDER), XML)
        self._store = SettingsStore(
            self._settings_file, TITLE, VERSION,
            preset_attributes=('name', 'pattern'))
        self.message(f'Settings loaded from {self._settings_file}')

        # Generate dict containing token names, shorthand, and values
        self.now = dt.datetime.now()
        self.tokens = {}
        self.generate_tokens()

        # Translate the token pattern to a regex
        self.pattern = ''
        self.load_pattern()

        # Translate the token pattern to a regex
        self.pattern_regex = ''
        self.generate_pattern_regex()

        # Find folders that match the regex
        self.folders = []
        self.find_folders()

        # Extract version token from the found folders
        self.version_padding = 0
        self.update_version_token()

        # Replace tokens to generate new folder name
        self.folder_new = ''
        self.resolve_tokens()

        # Windows
        self._windows = {
            'parent': self._get_flame_parent(),
            'main': None,
            'save': None,
        }
        self._windows['main'] = MainWindow(
            TITLE_VERSION, self._windows['parent'])
        self._windows['save'] = SavePresetWindow(self._windows['main'])

        # Window starting values
        self._windows['main'].preset = (
            self._store.preset_names[0] if self._store.preset_names else '')
        self._windows['main'].presets = self._store.preset_names
        self._windows['main'].pattern = self.pattern
        self._windows['main'].folder_new = self.folder_new
        self._windows['main'].tokens = {
            key: values[0] for key, values in self.tokens.items()}

        # Window signals
        self._windows['main'].signal_preset.connect(self._on_preset_change)
        self._windows['main'].signal_save.connect(self._on_preset_save)
        self._windows['main'].signal_delete.connect(self._on_preset_delete)
        self._windows['main'].signal_pattern.connect(self._on_pattern_change)
        self._windows['main'].signal_ok.connect(self._on_ok_clicked)
        self._windows['main'].signal_cancel.connect(self._on_cancel_clicked)

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

    def _on_preset_change(self):
        """Handle preset selection change; update pattern from store."""
        preset_name = self._windows['main'].preset
        if preset_name:
            preset = self._store.presets.get(preset_name)
            if preset:
                self.pattern = getattr(preset, 'pattern', '') or ''
                self._windows['main'].pattern = self.pattern
        self._refresh_folder_display()

    def _on_pattern_change(self, text):
        """Handle pattern text change; recompute folder and update display."""
        self.pattern = text
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
        self._windows['main'].preset = (
            self._store.preset_names[0] if self._store.preset_names else '')
        self._on_preset_change()

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

    def _refresh_folder_display(self):
        """Recompute folder name from pattern and update window display."""
        self.generate_pattern_regex()
        self.find_folders()
        self.update_version_token()
        self.resolve_tokens()
        self._windows['main'].folder_new = self.folder_new

    def generate_tokens(self):
        """Generate dictionary of tokens with a list for each.

        Each item has a list with the shorthand token, a token regex, a pattern
        regex and then the value.

        {name : [ token, token_regex, pattern_regex, value ], ...}

        name = full name of the token
        token = this is the shorthand used in the pattern. ie, {token}
        token_regex = optional regex to assist in generating the pattern regex.
            only necessary on tokens that take optional modifiers, ie.
            {version###}
        pattern_regex = regex to extract the token data from the folder name
        value = starting value
        """
        self.tokens = {
            'am/pm':
                ['{pp}', None, '[a-z]{2}', self.now.strftime('%p').lower()],
            'AM/PM':
                ['{PP}', None, '[A-Z]{2}', self.now.strftime('%p').upper()],
            'Day':
                ['{DD}', None, '[0-9]{2}', self.now.strftime('%d')],
            'Hour (12hr)':
                ['{hh}', None, '[0-9]{2}', self.now.strftime('%I')],
            'Hour (24hr)':
                ['{HH}', None, '[0-9]{2}', self.now.strftime('%H')],
            'Minute':
                ['{mm}', None, '[0-9]{2}', self.now.strftime('%M')],
            'Month':
                ['{MM}', None, '[0-9]{2}', self.now.strftime('%m')],
            'Version':
                # the regex for Version is a named capture group excluding zero
                # padding
                ['{version}', '{version#*}', '0*(?P<version>[1-9][0-9]*)', '1'],
            'Year (##)':
                ['{YY}', None, '[0-9]{2}', self.now.strftime('%y')],
            'Year (####)':
                ['{YYYY}', None, '[0-9]{4}', self.now.strftime('%Y')]}

    @staticmethod
    def capture_tokens(regex, folder):
        """Capture tokens using regex.

        Args:
            regex (str): regex that match tokens wrapped in curly braces
            folder (str): folder name to be tested

        Returns:
            Regex match object
        """
        try:
            result = re.match(regex, folder)
        except re.error:
            # for example, a situation where {version} is passed twice
            result = None

        return result

    def load_pattern(self):
        """Load the first preset's pattern or use the default pattern."""
        if self._store.preset_names:
            first_name = self._store.preset_names[0]
            preset = self._store.presets.get(first_name)
            self.pattern = (
                getattr(preset, 'pattern', '') or '{version}'
                if preset else '{version}')
        else:
            self.pattern = '{version}'

    def generate_pattern_regex(self):
        """Generate a regex based on the token pattern.

        This regex will be used to find matching folders.  Use the token regex
        if available otherwise just token.

        for example, {YYYY}_{MM}_{DD} would become [0-9]{4}_[0-9]{2}_[0-9]{2}
        """
        self.pattern_regex = self.pattern

        for token, values in self.tokens.items():
            del token
            if values[1]:  # token regex available
                self.pattern_regex = re.sub(values[1], values[2], self.pattern_regex)
            else:
                self.pattern_regex = re.sub(values[0], values[2], self.pattern_regex)

    def find_folders(self):
        """Appends tuples to self.folders list.

        The tuples contain the folder name, and then the version number if
        present.
        """
        # Always clear the list before searching again with new regex
        self.folders = []

        for folder in next(os.walk(self.path))[1]:
            search = self.capture_tokens(self.pattern_regex, folder)

            # append tuples containing matching folder name(str) and
            # version(int)
            match = []

            # folder name match
            if search:  # re returns match object or None
                match.append(search.group(0))

                # version token match
                # version must be integer because strings would sort as 1, 10,
                # 11, 9
                if len(search.groups()) == 1:  # groups only returns named groups
                    match.append(int(search.group(1)))

                self.folders.append(tuple(match))

    def update_version_token(self):
        """Scan for folder versions.

        Scan folders that matched the pattern regex to find if a version is
        present.  If so, find the highest version number and set value in
        self.tokens to be one higher.
        """

        def find_version_padding():
            """Find if the version number is padded with zeroes."""
            # find hashes preceeded by {version and trailed by }
            # using re.match starts searching from beginning of a string so
            # ?:.* is a non-capturing group for anything preceeding {version
            search = '(?:.*{version)(?P<padding>#*)}'

            result = self.capture_tokens(search, self.pattern)

            if result:
                self.version_padding = len(result.group(1))
            else:
                self.version_padding = 0

        find_version_padding()

        try:
            # sort self.folders by the second value in each set
            self.folders.sort(key=lambda item: item[1])
            version = self.folders[-1][1] + 1
        except IndexError:  # if there no folders with version matches
            version = 1

        self.tokens['Version'][3] = str(version).zfill(self.version_padding)

    def resolve_tokens(self):
        """Replace tokens with values."""
        self.folder_new = self.pattern

        for token, values in self.tokens.items():
            del token
            if values[1]:  # token regex available
                self.folder_new = re.sub(values[1], values[3], self.folder_new)
            else:
                self.folder_new = re.sub(values[0], values[3], self.folder_new)

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

    def _on_preset_save(self):
        """Show save preset dialog and save or overwrite preset on accept."""
        self._windows['save'].name = self._windows['main'].preset
        if self._windows['save'].exec_() != QtWidgets.QDialog.Accepted:
            return
        preset_name = self._windows['save'].name
        pattern = self.pattern
        duplicate = self._store.find_preset(preset_name) is not None
        if duplicate:
            if not FlameMessageWindow(
                    'Overwrite Existing Preset', 'confirm', 'Are you '
                    + 'sure want to permanently overwrite this preset?'
                    + '<br/>' + 'This operation cannot be undone.'):
                return
            self._store.overwrite_preset(name=preset_name, pattern=pattern)
        else:
            self._store.add_preset(name=preset_name, pattern=pattern)
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
        self._windows['main'].preset = preset_name


def scope_folder(selection):
    """Determine if selection is a single folder in the MediaHub > Files tab."""
    if len(selection) == 1 and isinstance(selection[0], flame.PyMediaHubFilesFolder):
        return True
    return False


def get_mediahub_files_custom_ui_actions():
    """Add right click menu items."""
    return [{'name': 'Create...',
             'actions': [{'name': 'Continue Folder',
                          'isVisible': scope_folder,
                          'execute': ContinueFolder,
                          'minimumVersion': '2025.0.0.0'}]
            }]
