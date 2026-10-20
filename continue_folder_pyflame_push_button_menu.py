"""PyFlame Push Button Menu Widget Module.

This module provides the PyFlamePushButtonMenu widget class for creating
Flame-themed push buttons with dropdown menus.

Credits:
    All the credit goes to Mike Vaglienty and his incredible PyFlame Library
    that he has very generously shared with us. You can find more information
    about the library and its usage at http://logik-portal.com/#pyflame/
"""

from collections.abc import Callable
from functools import partial

from PySide6 import QtCore, QtWidgets

from continue_folder_pyflame_colors import PyFlameColors


class PyFlamePushButtonMenu(QtWidgets.QPushButton):
    """Custom PyFlame Menu Push Button Widget.

    A custom push button widget with Flame-style theming that displays a
    dropdown menu of options. When a menu item is selected, the button text
    updates to show the selected option, and an optional callback function
    can be executed.

    Examples:
        Basic usage:
            >>> options = ['Option 1', 'Option 2', 'Option 3']
            >>> button = PyFlamePushButtonMenu('Select', options)

        With callback function:
            >>> def on_selection():
            ...     print('Option selected')
            >>> button = PyFlamePushButtonMenu(
            ...     'Select', options, menu_action=on_selection)

        Using first option as button name:
            >>> options = ['First', 'Second', 'Third']
            >>> button = PyFlamePushButtonMenu(options[0], options)

        Custom button dimensions:
            >>> button = PyFlamePushButtonMenu(
            ...     'Select', options, menu_width=300, menu_max_width=500)

    Note:
        The menu width automatically matches the button width when shown.
    """

    # Type hints for instance attributes
    menu: QtWidgets.QMenu

    def __init__(
            self,
            button_name: str,
            menu_options: list[str],
            menu_width: int = 240,
            menu_max_width: int = 2000,
            menu_action: Callable[[], None] | None = None
    ) -> None:
        """Initialize the PyFlamePushButtonMenu instance.

        Validates all parameters, stores instance variables, and initializes
        the button and menu widgets.

        Args:
            button_name: Text displayed on the button.
            menu_options: List of menu option strings. Each string will
                appear as a menu item. Can be empty (menu will have no
                items).
            menu_width: Minimum width of the button in pixels. Defaults to
                240.
            menu_max_width: Maximum width of the button in pixels. Defaults
                to 2000. Must be >= menu_width.
            menu_action: Optional callback function to execute when a menu
                item is selected. If provided, will be called after updating
                the button text to the selected option.

        Raises:
            TypeError: If menu_options is not a list or contains
                non-string elements.
            ValueError: If menu_width or menu_max_width are non-positive, or
                menu_max_width < menu_width.
        """
        super().__init__()

        # Validate parameters
        self._check_menu_options(menu_options)
        self._check_menu_dimensions(menu_width, menu_max_width)

        # Store instance variables
        self.menu_options = menu_options
        self.menu_action = menu_action

        # Initialize widgets
        self._init_button(button_name, menu_width, menu_max_width)
        self._init_menu(menu_options)

    def _init_button(
            self, button_name: str, menu_width: int, menu_max_width: int) -> None:
        """Initialize the button widget.

        Sets button text, dimensions, focus policy, and applies
        Flame-themed styling.

        Args:
            button_name: Text to display on the button.
            menu_width: Minimum width of the button in pixels.
            menu_max_width: Maximum width of the button in pixels.
        """
        self.setText(button_name)
        self.setMinimumHeight(28)
        self.setMinimumWidth(menu_width)
        self.setMaximumWidth(menu_max_width)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet(f"""
            QPushButton {{
                color: {PyFlameColors.TEXT_PRIMARY};
                background-color: {PyFlameColors.BG_WIDGET};
                border: none;
                font: 14px 'Discreet';
                padding-left: 9px;
                text-align: left}}
            QPushButton:disabled {{
                color: {PyFlameColors.TEXT_DISABLED};
                background-color: {PyFlameColors.BG_WIDGET};
                border: none}}
            QPushButton:hover {{
                border: 1px solid {PyFlameColors.BORDER_HOVER}}}
            QPushButton::menu-indicator {{image: none}}
            QToolTip {{
                color: {PyFlameColors.TEXT_TOOLTIP};
                background-color: {PyFlameColors.BG_MEDIUM};
                border: 10px solid {PyFlameColors.BG_MEDIUM}}}""")

    def _init_menu(self, menu_options: list[str]) -> None:
        """Initialize the menu widget.

        Creates the menu widget, applies Flame-themed styling, connects
        the width matching signal, populates menu items, and attaches the
        menu to the button.

        Args:
            menu_options: List of menu option strings to populate the
                menu with.
        """
        self.menu = QtWidgets.QMenu(self)
        self.menu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.menu.aboutToShow.connect(self._menu_match_width)
        self.menu.setStyleSheet(f"""
            QMenu {{
                color: {PyFlameColors.TEXT_PRIMARY};
                background-color: {PyFlameColors.BG_WIDGET};
                border: none;
                font: 14px 'Discreet'}}
            QMenu::item:selected {{
                color: {PyFlameColors.TEXT_SELECTED};
                background-color: {PyFlameColors.BG_SELECTED}}}""")
        self.populate_menu(menu_options)
        self.setMenu(self.menu)

    def _menu_change(
            self,
            option: str,
            menu_action: Callable[[], None] | None
    ) -> None:
        """Handle menu item selection.

        Updates the button text to the selected option and calls the
        optional menu_action callback if provided.

        Args:
            option: The selected menu option text.
            menu_action: Optional callback function to execute when
                option is selected.
        """
        self.setText(option)

        if menu_action:
            menu_action()

    def _menu_match_width(self) -> None:
        """Match menu width to the parent push button width.

        Called automatically when the menu is about to be shown. Ensures
        the menu width matches the current button width for a consistent
        visual appearance.

        Note:
            This method is connected to the menu's aboutToShow signal
            during initialization.
        """
        self.menu.setMinimumWidth(self.size().width())

    def populate_menu(self, menu_options: list[str]) -> None:
        """Empty the menu then reassemble the options.

        Args:
            menu_options: List of menu option strings. Must be a list
                containing only strings.

        Raises:
            TypeError: If menu_options is not a list or contains
                non-string elements.
            RuntimeError: If menu operations fail (e.g., menu widget is
                invalid or deleted).
        """
        self._check_menu_options(menu_options)
        self.menu_options = menu_options

        try:
            self.menu.clear()
        except (AttributeError, RuntimeError) as error:
            raise RuntimeError(
                'Cannot clear menu: menu widget is invalid or deleted') from error

        for option in menu_options:
            try:
                self.menu.addAction(
                    option, partial(self._menu_change, option, self.menu_action))
            except (AttributeError, RuntimeError) as error:
                raise RuntimeError(
                    f'Cannot add menu action for "{option}": menu widget is '
                    f'invalid or deleted') from error

    def _check_menu_options(self, menu_options: list[str]) -> None:
        """Validate menu_options parameter.

        Args:
            menu_options: List of menu option strings to validate.

        Raises:
            TypeError: If menu_options is not a list or contains
                non-string elements.
        """
        if not isinstance(menu_options, list):
            raise TypeError(
                f'menu_options must be a list, got {type(menu_options).__name__}')
        for option in menu_options:
            if not isinstance(option, str):
                raise TypeError(
                    f'menu_options must contain only strings, got '
                    f'{type(option).__name__}')

    def _check_menu_dimensions(
            self, menu_width: int, menu_max_width: int) -> None:
        """Validate menu dimension parameters.

        Args:
            menu_width: Minimum menu width to validate.
            menu_max_width: Maximum menu width to validate.

        Raises:
            ValueError: If dimensions are invalid (non-positive or
                max_width < width).
        """
        if menu_width <= 0:
            raise ValueError(
                f'menu_width must be positive, got {menu_width}')
        if menu_max_width <= 0:
            raise ValueError(
                f'menu_max_width must be positive, got {menu_max_width}')
        if menu_max_width < menu_width:
            raise ValueError(
                f'menu_max_width ({menu_max_width}) must be >= '
                f'menu_width ({menu_width})')
