"""PyFlame Push Button Widget Module.

This module provides the PyFlamePushButton widget class for creating
Flame-themed push buttons with toggle functionality.
"""

from PySide6 import QtCore, QtWidgets

from continue_folder_button_mixin import ButtonMixin
from continue_folder_pyflame_colors import PyFlameColors


class PyFlamePushButton(ButtonMixin, QtWidgets.QPushButton):
    """Custom PyFlame Push Button Widget.

    A custom push button widget with Flame-style theming that can be toggled
    between checked and unchecked states.

    Examples:
        Basic usage:
            >>> def on_click():
            ...     print('Button clicked')
            >>> button = PyFlamePushButton('Click Me', False)
            ...     button.clicked.connect(on_click)

        With checked state:
            >>> button = PyFlamePushButton('Toggle', True)

        Custom button dimensions:
            >>> button = PyFlamePushButton(
            ...     'Toggle', False, button_width=200, button_max_width=300)
    """

    # Type hints for instance attributes
    button_width: int
    button_max_width: int

    def __init__(
            self,
            name: str,
            checked: bool,
            button_width: int = 150,
            button_max_width: int = 150
    ) -> None:
        """Initialize the PyFlamePushButton instance.

        Validates all parameters, stores instance variables, and initializes
        the button UI components with Flame-themed styling.

        Args:
            name: Text displayed on the button.
            checked: Initial checked state of the button. If True, the button
                will appear in its checked state (highlighted).
            button_width: Minimum width of the button in pixels. Defaults to
                150.
            button_max_width: Maximum width of the button in pixels. Defaults
                to 150. Must be >= button_width.

        Raises:
            TypeError: If name is not a string, checked is not a bool.
            ValueError: If name is empty, or button_width or button_max_width
                are non-positive, or button_max_width < button_width.
        """
        super().__init__()

        # Validate parameters
        self._check_name(name)
        self._check_checked(checked)
        self._check_button_dimensions(button_width, button_max_width)

        # Store instance variables
        self.button_width = button_width
        self.button_max_width = button_max_width

        # Initialize UI components
        self._init_button(name, checked, button_width, button_max_width)

    def _check_name(self, name: str) -> None:
        """Validate name parameter.

        Args:
            name: Button text to validate.

        Raises:
            TypeError: If name is not a string.
            ValueError: If name is empty.
        """
        if not isinstance(name, str):
            raise TypeError(
                f'name must be a string, got {type(name).__name__}')
        if not name:
            raise ValueError('name cannot be empty')

    def _check_checked(self, checked: bool) -> None:
        """Validate checked parameter.

        Args:
            checked: Initial checked state to validate.

        Raises:
            TypeError: If checked is not a bool.
        """
        if not isinstance(checked, bool):
            raise TypeError(
                f'checked must be a bool, got {type(checked).__name__}')

    def _init_button(
            self,
            name: str,
            checked: bool,
            button_width: int,
            button_max_width: int
    ) -> None:
        """Initialize button UI components.

        Sets button properties, connects signals, sets dimensions, and
        applies Flame-themed styling.

        Args:
            name: Text to display on the button.
            checked: Initial checked state of the button.
            button_width: Minimum width of the button in pixels.
            button_max_width: Maximum width of the button in pixels.
        """
        # Set button properties
        self.setText(name)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set button dimensions
        self.setMinimumSize(QtCore.QSize(button_width, 28))
        self.setMaximumSize(QtCore.QSize(button_max_width, 28))

        # Apply stylesheet
        self.setStyleSheet(f"""
            QPushButton {{
                color: {PyFlameColors.TEXT_PRIMARY};
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 {PyFlameColors.BG_DARK},
                    stop: .94 {PyFlameColors.BORDER_ACCENT});
                text-align: left;
                border-top: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 {PyFlameColors.BG_DARK},
                    stop: .94 {PyFlameColors.BORDER_ACCENT});
                border-bottom: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 {PyFlameColors.BG_DARK},
                    stop: .94 {PyFlameColors.BORDER_ACCENT});
                border-left: 1px solid {PyFlameColors.BG_DARK};
                border-right: 1px solid {PyFlameColors.BORDER_ACCENT};
                padding-left: 5px;
                font: 14px 'Discreet'}}
            QPushButton:checked {{
                color: {PyFlameColors.TEXT_SELECTED};
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 {PyFlameColors.BG_MEDIUM},
                    stop: .94 {PyFlameColors.BORDER_CHECKED});
                text-align: left;
                border-top: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 {PyFlameColors.BG_MEDIUM},
                    stop: .94 {PyFlameColors.BORDER_CHECKED});
                border-bottom: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 {PyFlameColors.BG_MEDIUM},
                    stop: .94 {PyFlameColors.BORDER_CHECKED});
                border-left: 1px solid {PyFlameColors.BG_MEDIUM};
                border-right: 1px solid {PyFlameColors.BORDER_CHECKED};
                padding-left: 5px;
                font: italic}}
            QPushButton:hover {{
                border: 1px solid {PyFlameColors.BORDER_HOVER}}}
            QPushButton:disabled {{
                color: {PyFlameColors.TEXT_SECONDARY};
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 {PyFlameColors.BG_DARK},
                    stop: .94 {PyFlameColors.BG_DISABLED});
                font: light;
                border: none}}
            QToolTip {{
                color: {PyFlameColors.TEXT_TOOLTIP};
                background-color: {PyFlameColors.BG_MEDIUM};
                border: 10px solid {PyFlameColors.BG_MEDIUM}}}""")
