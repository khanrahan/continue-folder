"""Flame Button Widget Module.

This module provides the FlameButton widget class for creating Flame-themed
push buttons with callback functionality.
"""

from typing import Callable, Optional

from PySide6 import QtCore, QtWidgets  # pylint: disable=import-error

from continue_folder_flame_colors import FlameColors


class FlameButton(QtWidgets.QPushButton):
    """Custom Flame Button Widget.

    A custom push button widget with Flame-style theming that executes a
    callback function when clicked. The widget supports two color styles:
    normal (grey background) and blue (blue background). The widget is
    non-focusable and maintains a consistent height across all instances.

    Examples:
        Basic usage:
            >>> def do_something():
            ...     print('Button clicked')
            >>> button = FlameButton('Click Me', do_something)

        With blue color:
            >>> button = FlameButton(
            ...     'Click Me', do_something, button_color='blue')

        With custom width:
            >>> button = FlameButton(
            ...     'Click Me', do_something, button_width=200)

        With custom width and max width:
            >>> button = FlameButton(
            ...     'Click Me', do_something,
            ...     button_width=200, button_max_width=400)
    """

    _BUTTON_COLORS = ('normal', 'blue')
    _DEFAULT_HEIGHT = 28
    _DEFAULT_WIDTH = 150
    _DEFAULT_MAX_WIDTH = 150

    # Stylesheet constants
    _STYLESHEET_NORMAL = f"""
        QPushButton {{
            color: {FlameColors.TEXT_PRIMARY};
            background-color: {FlameColors.BG_DARK};
            border: none;
            font: 14px 'Discreet'}}
        QPushButton:hover {{
            border: 1px solid {FlameColors.BORDER_HOVER}}}
        QPushButton:pressed {{
            color: {FlameColors.TEXT_HOVER};
            background-color: {FlameColors.BG_PRESSED};
            border: 1px solid {FlameColors.BORDER_HOVER}}}
        QPushButton:disabled {{
            color: {FlameColors.TEXT_DISABLED};
            background-color: {FlameColors.BG_DARK};
            border: none}}
        QToolTip {{
            color: {FlameColors.TEXT_TOOLTIP};
            background-color: {FlameColors.BG_MEDIUM};
            border: 10px solid {FlameColors.BG_MEDIUM}}}"""

    _STYLESHEET_BLUE = f"""
        QPushButton {{
            color: {FlameColors.TEXT_BRIGHT};
            background-color: {FlameColors.BG_BLUE};
            border: none;
            font: 12px 'Discreet'}}
        QPushButton:hover {{
            border: 1px solid {FlameColors.BORDER_HOVER}}}
        QPushButton:pressed {{
            color: {FlameColors.TEXT_HOVER};
            border: 1px solid {FlameColors.BORDER_HOVER}}}
        QPushButton:disabled {{
            color: {FlameColors.TEXT_DISABLED};
            background-color: {FlameColors.BG_DARK};
            border: none}}
        QToolTip {{
            color: {FlameColors.TEXT_TOOLTIP};
            background-color: {FlameColors.BG_MEDIUM};
            border: 10px solid {FlameColors.BG_MEDIUM}}}"""

    def __init__(
            self,
            button_name: str,
            connect: Callable[[], None],
            button_color: str = 'normal',
            button_width: Optional[int] = None,
            button_max_width: Optional[int] = None
    ) -> None:
        """Initialize the FlameButton instance.

        Validates all parameters, applies default values if not provided, and
        initializes the widget properties with Flame-themed styling. The widget
        is configured as a non-focusable push button that executes a callback
        function when clicked.

        Args:
            button_name: Text to display on the button. Must be a non-empty
                string.
            connect: Callback function to execute when the button is clicked.
                Must be callable and cannot be None. The function should take
                no arguments.
            button_color: Style color for the button. Must be one of: 'normal'
                or 'blue'. Defaults to 'normal'. The 'normal' style uses a grey
                background, while 'blue' uses a blue background with slightly
                different font size.
            button_width: Minimum width of the button in pixels. If None,
                defaults to 150. Must be a positive integer.
            button_max_width: Maximum width of the button in pixels. If None,
                defaults to 150. Must be a positive integer and must be >=
                button_width.

        Raises:
            TypeError: If button_name is not a string, if connect is None or
                not callable, if button_color is not a string, or if
                button_width or button_max_width are not integers (when
                provided).
            ValueError: If button_name is empty, if button_color is not one of
                the allowed values, if button_width or button_max_width are not
                positive (when provided), or if button_width >
                button_max_width.
        """
        super().__init__()

        # Use default values if not provided
        if button_width is None:
            button_width = FlameButton._DEFAULT_WIDTH
        if button_max_width is None:
            button_max_width = FlameButton._DEFAULT_MAX_WIDTH

        # Validate parameters
        self._check_button_name(button_name)
        self._check_button_color(button_color)
        self._check_button_width(button_width)
        self._check_button_max_width(button_max_width)
        self._check_button_width_constraints(button_width, button_max_width)
        self._check_connect(connect)

        # Stylesheet mapping for button colors
        self._stylesheets = {
            'normal': FlameButton._STYLESHEET_NORMAL,
            'blue': FlameButton._STYLESHEET_BLUE
        }

        # Dimensions
        self.setMinimumSize(QtCore.QSize(button_width, self._DEFAULT_HEIGHT))
        self.setMaximumSize(QtCore.QSize(button_max_width, self._DEFAULT_HEIGHT))

        # Focus policy
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Text
        self.setText(button_name)

        # Signal connection
        self.clicked.connect(connect)

        # Stylesheet
        self.setStyleSheet(
            self._stylesheets.get(button_color, self._stylesheets['normal']))

    def _check_button_name(self, button_name: str) -> None:
        """Validate button_name parameter.

        Args:
            button_name: Button text to validate.

        Raises:
            TypeError: If button_name is not a string.
            ValueError: If button_name is empty.
        """
        if not isinstance(button_name, str):
            raise TypeError(
                f'button_name must be a string, got {type(button_name).__name__}')
        if not button_name:
            raise ValueError('button_name cannot be empty')

    def _check_connect(self, connect: Callable[[], None]) -> None:
        """Validate connect parameter.

        Args:
            connect: Callback function to validate.

        Raises:
            TypeError: If connect is None or not callable.
        """
        if connect is None:
            raise TypeError('connect cannot be None')
        if not callable(connect):
            raise TypeError(
                f'connect must be callable, got {type(connect).__name__}')

    def _check_button_color(self, button_color: str) -> None:
        """Validate button_color parameter.

        Args:
            button_color: Button color to validate.

        Raises:
            TypeError: If button_color is not a string.
            ValueError: If button_color is not one of the allowed values.
        """
        if not isinstance(button_color, str):
            raise TypeError(
                f'button_color must be a string, got {type(button_color).__name__}')
        if button_color not in FlameButton._BUTTON_COLORS:
            raise ValueError(
                f'button_color must be one of: '
                f'{", ".join(FlameButton._BUTTON_COLORS)}. '
                f'Got {button_color}')

    def _check_button_width(self, button_width: int) -> None:
        """Validate button_width parameter.

        Args:
            button_width: Button width to validate.

        Raises:
            TypeError: If button_width is not an integer.
            ValueError: If button_width is not positive.
        """
        if not isinstance(button_width, int):
            raise TypeError(
                f'button_width must be an integer, got {type(button_width).__name__}')
        if button_width <= 0:
            raise ValueError(
                f'button_width must be positive, got {button_width}')

    def _check_button_max_width(self, button_max_width: int) -> None:
        """Validate button_max_width parameter.

        Args:
            button_max_width: Button maximum width to validate.

        Raises:
            TypeError: If button_max_width is not an integer.
            ValueError: If button_max_width is not positive.
        """
        if not isinstance(button_max_width, int):
            raise TypeError(
                f'button_max_width must be an integer, '
                f'got {type(button_max_width).__name__}')
        if button_max_width <= 0:
            raise ValueError(
                f'button_max_width must be positive, got {button_max_width}')

    def _check_button_width_constraints(
            self, button_width: int, button_max_width: int) -> None:
        """Validate button width constraint relationship.

        Args:
            button_width: Button width to validate.
            button_max_width: Button maximum width to validate.

        Raises:
            ValueError: If button_width > button_max_width.
        """
        if button_width > button_max_width:
            raise ValueError(
                f'button_width ({button_width}) must be <= button_max_width '
                f'({button_max_width})')
