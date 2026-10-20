"""PyFlame Colors Module.

This module provides centralized color constants for PyFlame UI styling.

Credits:
    All the credit goes to Mike Vaglienty and his incredible PyFlame Library
    that he has very generously shared with us. You can find more information
    about the library and its usage at http://logik-portal.com/#pyflame/
"""


class PyFlameColors:
    """Centralized color constants for PyFlame UI styling.

    Provides RGB color values as formatted strings for use in Qt stylesheets.
    Colors are organized by usage category.
    """

    # Text colors
    TEXT_PRIMARY = 'rgb(154, 154, 154)'  # Main text color
    TEXT_SECONDARY = 'rgb(106, 106, 106)'  # Disabled/secondary text
    TEXT_BRIGHT = 'rgb(190, 190, 190)'  # Bright text (blue buttons)
    TEXT_HOVER = 'rgb(159, 159, 159)'  # Hover state text
    TEXT_DISABLED = 'rgb(116, 116, 116)'  # Disabled text
    TEXT_SELECTED = 'rgb(217, 217, 217)'  # Selected/checked text
    TEXT_TOOLTIP = 'rgb(170, 170, 170)'  # Tooltip text
    TEXT_ALTERNATE = 'rgb(137, 137, 137)'  # Alternate text color
    TEXT_PRESSED = 'rgb(187, 187, 187)'  # Pressed state text
    TEXT_TABLE_HEADER = 'rgb(177, 177, 177)'  # Table header text

    # Background colors
    BG_DARK = 'rgb(58, 58, 58)'  # Dark background
    BG_DARKER = 'rgb(36, 36, 36)'  # Darker background
    BG_DARKEST = 'rgb(33, 33, 33)'  # Darkest background
    BG_MEDIUM = 'rgb(71, 71, 71)'  # Medium background
    BG_PRESSED = 'rgb(66, 66, 66)'  # Pressed background
    BG_DISABLED = 'rgb(55, 55, 55)'  # Disabled background
    BG_BLUE = 'rgb(0, 110, 175)'  # Blue button background
    BG_SELECTED = 'rgb(58, 69, 81)'  # Selected item background
    BG_WIDGET = 'rgb(45, 55, 68)'  # Widget background
    BG_WIDGET_LIGHT = 'rgb(55, 65, 75)'  # Light widget background
    BG_LINEEDIT = 'rgb(55, 62, 71)'  # LineEdit background
    BG_LINEEDIT_FOCUS = 'rgb(73, 86, 99)'  # LineEdit focus background
    BG_LINEEDIT_PRESSED = 'rgb(71, 78, 88)'  # LineEdit pressed background
    BG_LABEL = 'rgb(30, 30, 30)'  # Label background
    BG_TABLE_HEADER = 'rgb(19, 21, 23)'  # Table header background

    # Border colors
    BORDER_HOVER = 'rgb(90, 90, 90)'  # Hover border
    BORDER_LABEL = 'rgb(40, 40, 40)'  # Label border
    BORDER_ACCENT = 'rgb(44, 54, 68)'  # Accent border
    BORDER_CHECKED = 'rgb(50, 101, 173)'  # Checked border

    # Selection colors
    SELECTION_TEXT = 'rgb(38, 38, 38)'  # Selection text
    SELECTION_BG = 'rgb(184, 177, 167)'  # Selection background
