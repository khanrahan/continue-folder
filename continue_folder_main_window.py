"""Main Window Module.

This module provides the MainWindow widget class for the main application
interface.
"""

from typing import Optional

from PySide6 import QtCore, QtWidgets  # pylint: disable=import-error

from continue_folder_flame_button import FlameButton
from continue_folder_flame_label import FlameLabel
from continue_folder_flame_line_edit import FlameLineEdit
from continue_folder_flame_push_button import FlamePushButton
from continue_folder_flame_push_button_menu import FlamePushButtonMenu
from continue_folder_flame_token_push_button import FlameTokenPushButton
from continue_folder_window_mixin import WindowMixin


class MainWindow(WindowMixin, QtWidgets.QWidget):
    """Main application window for Continue Folder.

    This class provides the primary interface for the application, including:
    - Preset selection and management (save/delete)
    - Pattern input field with token insertion
    - New folder name display
    - Destination selection (Desktop Reel / MediaHub Folder)
    - OK/Cancel action buttons

    The window uses Qt signals to communicate user interactions to the
    controller class (ContinueFolder), following a view-controller pattern.

    Attributes:
        signal_preset: Emitted when preset selection changes.
        signal_save: Emitted when Save preset button is clicked.
        signal_delete: Emitted when Delete preset button is clicked.
        signal_pattern: Emitted when pattern line edit text changes.
        signal_ok: Emitted when OK button is clicked.
        signal_cancel: Emitted when Cancel button is clicked.
    """
    signal_preset = QtCore.Signal()
    signal_save = QtCore.Signal()
    signal_delete = QtCore.Signal()
    signal_pattern = QtCore.Signal(str)
    signal_ok = QtCore.Signal()
    signal_cancel = QtCore.Signal()

    _WINDOW_X = 900
    _WINDOW_Y = 130

    def __init__(
            self,
            title_version: str,
            parent_widget: Optional[QtWidgets.QWidget] = None
    ) -> None:
        """Initialize the main window instance.

        Args:
            title_version: Window title string to display.
            parent_widget: Optional parent Qt widget.

        Note:
            PySide can behave unexpectedly when a parent widget is not
            provided. For example, the MainWindow could get lost behind the
            Flame app window.
        """
        super().__init__(parent=parent_widget)
        self.title_version = title_version
        self._labels = {}
        self._line_edits = {}
        self._buttons = {}
        self._layouts = {}
        self._init_window()

    def _init_labels(self) -> None:
        """Initialize all label widgets used in the window."""
        self._labels['preset'] = FlameLabel('Preset', 'normal')
        self._labels['pattern'] = FlameLabel('Pattern', 'normal')
        self._labels['folder'] = FlameLabel('New Folder', 'normal')
        self._labels['destination'] = FlameLabel('Destination', 'normal')

    def _init_line_edits(self) -> None:
        """Initialize all line edit and read-only folder display."""
        self._line_edits['pattern'] = FlameLineEdit('')
        self._line_edits['pattern'].textChanged.connect(self.signal_pattern.emit)
        self._line_edits['folder'] = FlameLineEdit('')

    def _init_buttons(self) -> None:
        """Initialize all button widgets used in the window."""
        self._buttons['preset'] = FlamePushButtonMenu(
            '',
            [],
            menu_action=self.signal_preset.emit,
        )
        self._buttons['preset'].setMaximumSize(QtCore.QSize(4000, 28))

        self._buttons['preset_save'] = FlameButton(
            'Save', self.signal_save.emit, button_width=110)
        self._buttons['preset_delete'] = FlameButton(
            'Delete', self.signal_delete.emit, button_width=110)

        self._buttons['tokens'] = FlameTokenPushButton(
            'Add Token',
            {},
            self._line_edits['pattern'],
        )

        self._buttons['ok'] = FlameButton(
            'Ok', self.signal_ok.emit, button_color='blue', button_width=110)
        self._buttons['cancel'] = FlameButton(
            'Cancel', self.signal_cancel.emit, button_width=110)

        self._buttons['destination_reel'] = FlamePushButton('Desktop Reel', True)
        self._buttons['destination_folder'] = FlamePushButton('MediaHub Folder', False)

    def _init_layouts(self) -> None:
        """Initialize and configure all layout managers for the window."""
        self._layouts['hbox1'] = QtWidgets.QHBoxLayout()
        self._layouts['hbox1'].addWidget(self._buttons['destination_reel'])
        self._layouts['hbox1'].addWidget(self._buttons['destination_folder'])
        self._layouts['hbox1'].addStretch()

        self._layouts['grid'] = QtWidgets.QGridLayout()
        self._layouts['grid'].setVerticalSpacing(10)
        self._layouts['grid'].setHorizontalSpacing(10)
        self._layouts['grid'].addWidget(self._labels['preset'], 0, 0)
        self._layouts['grid'].addWidget(self._buttons['preset'], 0, 1)
        self._layouts['grid'].addWidget(self._buttons['preset_save'], 0, 2)
        self._layouts['grid'].addWidget(self._buttons['preset_delete'], 0, 3)
        self._layouts['grid'].addWidget(self._labels['pattern'], 1, 0)
        self._layouts['grid'].addWidget(self._line_edits['pattern'], 1, 1)
        self._layouts['grid'].addWidget(self._buttons['tokens'], 1, 2)
        self._layouts['grid'].addWidget(self._labels['folder'], 2, 0)
        self._layouts['grid'].addWidget(self._line_edits['folder'], 2, 1)
        self._layouts['grid'].addWidget(self._labels['destination'], 3, 0)
        self._layouts['grid'].addLayout(self._layouts['hbox1'], 3, 1)

        self._layouts['hbox2'] = QtWidgets.QHBoxLayout()
        self._layouts['hbox2'].addStretch(1)
        self._layouts['hbox2'].addWidget(self._buttons['cancel'])
        self._layouts['hbox2'].addWidget(self._buttons['ok'])

        self._layouts['vbox'] = QtWidgets.QVBoxLayout()
        self._layouts['vbox'].setContentsMargins(20, 20, 20, 20)
        self._layouts['vbox'].addLayout(self._layouts['grid'])
        self._layouts['vbox'].addSpacing(20)
        self._layouts['vbox'].addLayout(self._layouts['hbox2'])

    def _init_window(self) -> None:
        """Build and configure the complete window interface."""
        self.setMinimumSize(self._WINDOW_X, self._WINDOW_Y)
        self.setStyleSheet('background-color: #272727')
        self.setWindowTitle(self.title_version)

        # Mac needs this to close the window
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Keeps on top of Flame but not other windows
        self.setWindowFlags(QtCore.Qt.Tool)

        # Widgets
        self._init_labels()
        self._init_line_edits()
        self._init_buttons()

        # layouts
        self._init_layouts()
        self.setLayout(self._layouts['vbox'])
        self._center_window()

    @property
    def preset(self) -> str:
        """Get or set the currently selected preset name."""
        return self._buttons['preset'].text()

    @preset.setter
    def preset(self, string: str) -> None:
        self._buttons['preset'].setText(string)

    @property
    def presets(self) -> list:
        """Get or set the list of available preset names."""
        return getattr(
            self._buttons['preset'], 'menu_options',
            [])

    @presets.setter
    def presets(self, preset_list: list) -> None:
        self._buttons['preset'].populate_menu(preset_list)

    @property
    def pattern(self) -> str:
        """Get or set the current pattern value."""
        return self._line_edits['pattern'].text()

    @pattern.setter
    def pattern(self, string: str) -> None:
        self._line_edits['pattern'].setText(string)

    @property
    def folder_new(self) -> str:
        """Get or set the new folder name display."""
        return self._line_edits['folder'].text()

    @folder_new.setter
    def folder_new(self, string: str) -> None:
        self._line_edits['folder'].setText(string)

    @property
    def tokens(self) -> dict:
        """Get or set the token dict for the Add Token button."""
        return getattr(self._buttons['tokens'], 'token_dict', {})

    @tokens.setter
    def tokens(self, token_dict: dict) -> None:
        self._buttons['tokens'].populate_menu(token_dict)

    @property
    def destination_reel_checked(self) -> bool:
        """Return True if Desktop Reel is selected."""
        return self._buttons['destination_reel'].isChecked()

    @property
    def destination_folder_checked(self) -> bool:
        """Return True if MediaHub Folder is selected."""
        return self._buttons['destination_folder'].isChecked()
