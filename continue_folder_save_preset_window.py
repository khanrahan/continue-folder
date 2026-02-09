"""Save Preset Window Module.

This module provides the SavePresetWindow dialog class for saving preset
configurations with a name.
"""

from typing import Optional

from continue_folder_flame_button import FlameButton
from confinue_folder_flame_label import FlameLabel
from continue_folder_flame_line_edit import FlameLineEdit
from PySide6 import QtGui, QtWidgets  # pylint: disable=import-error


class SavePresetWindow(QtWidgets.QDialog):
    """Dialog window for saving presets with a name.

    This dialog provides a simple interface for users to enter a name when
    saving a preset configuration. It displays a text input field for the
    preset name and Save/Cancel buttons.

    The dialog is modal, meaning it blocks interaction with the parent window
    until the user either accepts (Save) or rejects (Cancel) the dialog.

    Usage:
        The dialog should be shown using exec() or exec_(). After the dialog
        closes, check the return value:
        - QDialog.Accepted: User clicked Save
        - QDialog.Rejected: User clicked Cancel

        Access the entered name via the `name` property.

    Example:
        >>> window = SavePresetWindow(parent_widget)
        >>> window.name = 'Default Preset'  # Pre-fill the name
        >>> if window.exec() == QtWidgets.QDialog.Accepted:
        ...     preset_name = window.name
        ...     # Save the preset with this name
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget]) -> None:
        """Initialize the save preset dialog window.

        Args:
            parent: Optional parent Qt widget.

        Note:
            PySide can behave unexpectedly when a parent widget is not
            provided. For example, the MainWindow could get lost behind the
            Flame app window.
        """
        super().__init__(parent)
        self.dimensions = {'x': 500, 'y': 100}
        self._labels = {}
        self._line_edits = {}
        self._buttons = {}
        self._layouts = {}
        self._init_window()

    def _init_widgets(self) -> None:
        """Initialize all widgets used in the window."""
        # Labels
        self._labels['preset_name'] = FlameLabel('Preset Name', 'normal')

        # Line Edits
        self._line_edits['preset_name'] = FlameLineEdit('')

        # Buttons
        self._buttons['save'] = FlameButton(
            'Save', self.accept, button_color='blue', button_width=110)
        self._buttons['cancel'] = FlameButton(
            'Cancel', self.reject, button_width=110)

    def _init_layouts(self):
        """Initialize all layouts used in the window."""
        self._layouts['grid'] = QtWidgets.QGridLayout()
        self._layouts['grid'].setVerticalSpacing(10)
        self._layouts['grid'].setHorizontalSpacing(10)
        self._layouts['grid'].addWidget(self._labels['preset_name'], 0, 0)
        self._layouts['grid'].addWidget(self._line_edits['preset_name'], 0, 1)

        self._layouts['hbox'] = QtWidgets.QHBoxLayout()
        self._layouts['hbox'].addStretch(1)
        self._layouts['hbox'].addWidget(self._buttons['cancel'])
        self._layouts['hbox'].addWidget(self._buttons['save'])

        self._layouts['vbox'] = QtWidgets.QVBoxLayout()
        self._layouts['vbox'].setContentsMargins(20, 20, 20, 20)
        self._layouts['vbox'].addLayout(self._layouts['grid'])
        self._layouts['vbox'].addSpacing(20)
        self._layouts['vbox'].addLayout(self._layouts['hbox'])

    def _init_window(self) -> None:
        """Initialize the window."""
        self.setMinimumSize(
                self.dimensions['x'], self.dimensions['y'])

        self.setStyleSheet('background-color: #272727')
        self.setWindowTitle('Save Preset As...')

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().screenGeometry()
        self.move(
            (resolution.width() / 2) - (self.dimensions['x'] / 2),
            (resolution.height() / 2) - (self.dimensions['y'] / 2 + 44))

        self._init_widgets()
        self._init_layouts()
        self.setLayout(self._layouts['vbox'])

    @property
    def name(self) -> str:
        """Get the preset name."""
        return self._line_edits['preset_name'].text()

    @name.setter
    def name(self, string: str) -> None:
        """Set the present name."""
        self._line_edits['preset_name'].setText(string)
