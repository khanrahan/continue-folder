"""Flame Label Widget Module.

This module provides the FlameLabel widget class for creating Flame-themed
label widgets with customizable styling.
"""


from PySide6 import QtCore, QtWidgets  # pylint: disable=import-error

from continue_folder_flame_colors import FlameColors


class FlameLabel(QtWidgets.QLabel):
    """Custom Flame Label Widget.

    A custom label widget with Flame-style theming that displays text with
    customizable styling. The widget supports three style types: normal,
    underline (centered text with bottom border), and background (with
    background color and padding). The widget is non-focusable and maintains
    a consistent height across all instances.

    Examples:
        Basic usage:
            >>> label = FlameLabel('Label Name')

        With underline style:
            >>> label = FlameLabel('Section Title', 'underline')

        With background style and custom width:
            >>> label = FlameLabel('Header', 'background', 300)

        Custom width only:
            >>> label = FlameLabel('Label Text', label_width=250)
    """
    _DEFAULT_WIDTH = 150
    _LABEL_TYPES = ('normal', 'underline', 'background')
    _MINIMUM_HEIGHT = 28

    # Stylesheet constants
    _STYLESHEET_NORMAL = f"""
        QLabel {{
            color: {FlameColors.TEXT_PRIMARY};
            font: 14px 'Discreet'}}
        QLabel:disabled {{
            color: {FlameColors.TEXT_SECONDARY}}}"""

    _STYLESHEET_UNDERLINE = f"""
        QLabel {{
            color: {FlameColors.TEXT_PRIMARY};
            border-bottom: 1px inset {FlameColors.BORDER_LABEL};
            font: 14px 'Discreet'}}
        QLabel:disabled {{
            color: {FlameColors.TEXT_SECONDARY}}}"""

    _STYLESHEET_BACKGROUND = f"""
        QLabel {{
            color: {FlameColors.TEXT_PRIMARY};
            background-color: {FlameColors.BG_LABEL};
            padding-left: 5px;
            font: 14px 'Discreet'}}
        QLabel:disabled {{
            color: {FlameColors.TEXT_SECONDARY}}}"""

    def __init__(
            self,
            label_name: str,
            label_type: str = 'normal',
            label_width: int | None = None
    ) -> None:
        """Initialize the FlameLabel instance.

        Validates all parameters, applies default values if not provided, and
        initializes the widget properties with Flame-themed styling.

        Args:
            label_name: Text to display in the label. Must be a non-empty
                string.
            label_type: Style type for the label. Must be one of: 'normal',
                'underline', or 'background'. Defaults to 'normal'. The
                'underline' type centers the text and adds a bottom border.
                The 'background' type adds a background color and left padding.
            label_width: Minimum width of the label in pixels. If None,
                defaults to 150. Must be a positive integer.

        Raises:
            TypeError: If label_name is not a string, if label_type is not a
                string, or if label_width is not an integer (when provided).
            ValueError: If label_name is empty, if label_type is not one of the
                allowed values, or if label_width is not positive (when
                provided).
        """
        super().__init__()

        # Validate parameters
        self._check_label_name(label_name)
        self._check_label_type(label_type)

        # Use default value if not provided
        if label_width is None:
            label_width = FlameLabel._DEFAULT_WIDTH
        self._check_label_width(label_width)

        # Stylesheet mapping for label types
        self._stylesheets = {
            'normal': FlameLabel._STYLESHEET_NORMAL,
            'underline': FlameLabel._STYLESHEET_UNDERLINE,
            'background': FlameLabel._STYLESHEET_BACKGROUND
        }

        # Dimensions
        self.setMinimumSize(label_width, self._MINIMUM_HEIGHT)
        self.setMaximumHeight(self._MINIMUM_HEIGHT)

        # Focus policy
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Text
        self.setText(label_name)

        # Alignment (only for underline type)
        if label_type == 'underline':
            self.setAlignment(QtCore.Qt.AlignCenter)

        # Stylesheet
        self.setStyleSheet(
            self._stylesheets.get(label_type, self._stylesheets['normal']))

    def _check_label_name(self, label_name: str) -> None:
        """Validate label_name parameter.

        Args:
            label_name: Label text to validate.

        Raises:
            TypeError: If label_name is not a string.
        """
        if not isinstance(label_name, str):
            raise TypeError(
                f'label_name must be a string, got {type(label_name).__name__}')

    def _check_label_type(self, label_type: str) -> None:
        """Validate label_type parameter.

        Args:
            label_type: Label type to validate.

        Raises:
            TypeError: If label_type is not a string.
            ValueError: If label_type is not one of the allowed values.
        """
        if not isinstance(label_type, str):
            raise TypeError(
                f'label_type must be a string, got {type(label_type).__name__}')
        if label_type not in FlameLabel._LABEL_TYPES:
            raise ValueError(
                f'label_type must be one of: {", ".join(FlameLabel._LABEL_TYPES)}. '
                f'Got {label_type}')

    def _check_label_width(self, label_width: int) -> None:
        """Validate label_width parameter.

        Args:
            label_width: Label width to validate.

        Raises:
            TypeError: If label_width is not an integer.
            ValueError: If label_width is not positive.
        """
        if not isinstance(label_width, int):
            raise TypeError(
                f'label_width must be an integer, got {type(label_width).__name__}')
        if label_width <= 0:
            raise ValueError(
                f'label_width must be positive, got {label_width}')
