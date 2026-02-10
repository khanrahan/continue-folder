"""Flame Line Edit Widget Module.

This module provides the FlameLineEdit widget class for creating Flame-themed
line edit widgets with customizable width constraints.
"""

from typing import Optional

from PySide6 import QtCore, QtWidgets  # pylint: disable=import-error

from continue_folder_flame_colors import FlameColors


class FlameLineEdit(QtWidgets.QLineEdit):
    """Custom Flame Line Edit Widget.

    A custom line edit widget with Flame-style theming that provides a
    text input field with customizable width constraints. The widget supports
    focus highlighting and hover effects, and is designed to integrate
    seamlessly with Flame's UI styling.

    Examples:
        Basic usage:
            >>> line_edit = FlameLineEdit('Some text here')

        With custom width:
            >>> line_edit = FlameLineEdit('Enter value', width=300)

        With custom width and max width:
            >>> line_edit = FlameLineEdit(
            ...     'Enter value', width=200, max_width=500)
    """

    _DEFAULT_MAX_WIDTH = 2000
    _DEFAULT_WIDTH = 150
    _MINIMUM_HEIGHT = 28
    _STYLESHEET = f"""
        QLineEdit {{
            color: {FlameColors.TEXT_PRIMARY};
            background-color: {FlameColors.BG_WIDGET_LIGHT};
            selection-color: {FlameColors.SELECTION_TEXT};
            selection-background-color: {FlameColors.SELECTION_BG};
            border: 1px solid {FlameColors.BG_WIDGET_LIGHT};
            padding-left: 5px;
            font: 14px 'Discreet'}}
        QLineEdit:focus {{
            background-color: {FlameColors.BG_LINEEDIT_FOCUS}}}
        QLineEdit:hover {{
            border: 1px solid {FlameColors.BORDER_HOVER}}}
        QLineEdit:disabled {{
            color: {FlameColors.TEXT_SECONDARY};
            background-color: {FlameColors.BG_DISABLED};
            border: 1px solid {FlameColors.BG_DISABLED}}}
        QToolTip {{
            color: {FlameColors.TEXT_TOOLTIP};
            background-color: {FlameColors.BG_MEDIUM};
            border: none}}"""

    def _check_text(self, text: str) -> None:
        """Validate text parameter.

        Args:
            text: Text string to validate.

        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(
                f'text must be a string, got {type(text).__name__}')

    def _check_width(self, width: int) -> None:
        """Validate width parameter.

        Args:
            width: Widget width to validate.

        Raises:
            TypeError: If width is not an integer.
            ValueError: If width is not positive.
        """
        if not isinstance(width, int):
            raise TypeError(
                f'width must be an integer, got {type(width).__name__}')
        if width <= 0:
            raise ValueError(
                f'width must be positive, got {width}')

    def _check_max_width(self, max_width: int) -> None:
        """Validate max_width parameter.

        Args:
            max_width: Maximum widget width to validate.

        Raises:
            TypeError: If max_width is not an integer.
            ValueError: If max_width is not positive.
        """
        if not isinstance(max_width, int):
            raise TypeError(
                f'max_width must be an integer, got {type(max_width).__name__}')
        if max_width <= 0:
            raise ValueError(
                f'max_width must be positive, got {max_width}')

    def _check_width_constraints(self, width: int, max_width: int) -> None:
        """Validate width constraint relationship.

        Args:
            width: Widget width to validate.
            max_width: Maximum widget width to validate.

        Raises:
            ValueError: If width > max_width.
        """
        if width > max_width:
            raise ValueError(
                f'width ({width}) must be <= max_width ({max_width})')

    def __init__(
            self,
            text: str,
            width: Optional[int] = None,
            max_width: Optional[int] = None
    ) -> None:
        """Initialize the FlameLineEdit instance.

        Validates all parameters, applies default values if not provided, and
        initializes the widget properties with Flame-themed styling. The widget
        is configured as an editable line edit with click focus policy.

        Qt.StrongFocus sets the widget to receive focus via both mouse clicks
        and key presses.

        Args:
            text: Initial text to display in the line edit widget. Can be an
                empty string.
            width: Minimum width of the widget in pixels. If None, defaults to
                150. Must be a positive integer.
            max_width: Maximum width of the widget in pixels. If None, defaults
                to 2000. Must be a positive integer and must be >= width.

        Raises:
            TypeError: If text is not a string, or if width or max_width are
                not integers (when provided).
            ValueError: If width or max_width are not positive (when provided),
                or if width > max_width.
        """
        super().__init__()

        # Use default values if not provided
        if width is None:
            width = FlameLineEdit._DEFAULT_WIDTH
        if max_width is None:
            max_width = FlameLineEdit._DEFAULT_MAX_WIDTH

        # Validate parameters
        self._check_text(text)
        self._check_width(width)
        self._check_max_width(max_width)
        self._check_width_constraints(width, max_width)

        # Dimensions
        self.setMinimumHeight(self._MINIMUM_HEIGHT)
        self.setMinimumWidth(width)
        self.setMaximumWidth(max_width)

        # Focus policy
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Text
        self.setText(text)

        # Stylesheet
        self.setStyleSheet(self._STYLESHEET)
