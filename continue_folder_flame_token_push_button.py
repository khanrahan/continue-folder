"""Flame Token Push Button Widget Module.

This module provides the FlameTokenPushButton widget class for creating
Flame-themed push buttons with token dropdown menus.
"""

from functools import partial

from PySide6 import QtCore, QtWidgets

from continue_folder_button_mixin import ButtonMixin
from continue_folder_flame_colors import FlameColors


class FlameTokenPushButton(ButtonMixin, QtWidgets.QPushButton):
    """Custom Flame Token Push Button Widget.

    A custom push button widget with Flame-style theming that displays a
    dropdown menu of tokens. When a token is selected from the menu, it is
    inserted into the specified LineEdit widget at the current cursor
    position.

    Examples:
        Basic usage:
            >>> token_dict = {
            ...     'Project Name': '<project>',
            ...     'Shot Name': '<shot>',
            ...     'User Name': '<user>'
            ... }
            >>> line_edit = QtWidgets.QLineEdit()
            >>> button = FlameTokenPushButton(
            ...     'Add Token', token_dict, line_edit)

        With sorting enabled:
            >>> button = FlameTokenPushButton(
            ...     'Add Token', token_dict, line_edit, sort=True)

        Custom button dimensions:
            >>> button = FlameTokenPushButton(
            ...     'Add Token', token_dict, line_edit,
            ...     button_width=150, button_max_width=400)
    """

    # Type hints for instance attributes
    button_name: str
    token_dict: dict[str, str]
    token_dest: QtWidgets.QLineEdit
    button_width: int
    button_max_width: int
    sort: bool
    token_menu: QtWidgets.QMenu

    def __init__(
            self,
            button_name: str,
            token_dict: dict[str, str],
            token_dest: QtWidgets.QLineEdit,
            button_width: int = 110,
            button_max_width: int = 300,
            sort: bool = False
    ) -> None:
        """Initialize the FlameTokenPushButton instance.

        Validates all parameters, stores instance variables, and initializes
        the button UI components.

        Args:
            button_name: Text displayed on the button.
            token_dict: Dictionary mapping token display names to token values.
                Keys are the names shown in the menu, values are the tokens
                inserted into the LineEdit. Format: {'Display Name':
                '<Token>'}.
            token_dest: LineEdit widget where selected tokens will be inserted.
            button_width: Minimum width of the button in pixels. Defaults to
                110.
            button_max_width: Maximum width of the button in pixels. Defaults
                to 300. Must be >= button_width.
            sort: If True, sorts tokens in the menu case-insensitively first,
                then by case (lowercase precedes uppercase). Defaults to False.

        Raises:
            ValueError: If token_dest is None, button_width or
                button_max_width are non-positive, or button_max_width <
                button_width.
            TypeError: If token_dict keys or values are not strings.
        """
        super().__init__()

        # Validate parameters
        self._check_token_dict(token_dict)
        self._check_token_dest(token_dest)
        self._check_button_dimensions(button_width, button_max_width)

        # Store instance variables
        self.button_name = button_name
        self.token_dict = token_dict
        self.token_dest = token_dest
        self.button_width = button_width
        self.button_max_width = button_max_width
        self.sort = sort

        # Initialize UI components
        self._init_button()
        self.populate_menu(self.token_dict)

    def _check_token_dict(self, token_dict: dict[str, str]) -> None:
        """Validate token_dict parameter.

        Args:
            token_dict: Dictionary to validate. Can be empty (button will
                have no menu items until populated).

        Raises:
            TypeError: If keys or values are not strings.
        """
        for key, value in token_dict.items():
            if not isinstance(key, str):
                raise TypeError(
                    f'token_dict keys must be strings, got {type(key).__name__}')
            if not isinstance(value, str):
                raise TypeError(
                    f'token_dict values must be strings, got {type(value).__name__}')

    def _check_token_dest(self, token_dest: QtWidgets.QLineEdit) -> None:
        """Validate token_dest parameter.

        Args:
            token_dest: LineEdit widget to validate.

        Raises:
            ValueError: If token_dest is None.
        """
        if token_dest is None:
            raise ValueError('token_dest cannot be None')

    def _get_token_names_sorted(self, item: tuple[str, str]) -> tuple[str, bool]:
        """Get sorted keys for token items.

        Sorts tokens case-insensitively first, then by case (lowercase
        precedes uppercase). For example: aa, AA, bb, BB, cc, CC.

        Args:
            item: Tuple of (token_name, token_value).

        Returns:
            Tuple of (uppercase_name, is_uppercase) for sorting.
        """
        name, _ = item
        return (name.upper(), name.isupper())

    def _init_button(self) -> None:
        """Initialize the button."""
        self.setText(self.button_name)
        self.setMinimumHeight(28)
        self.setMinimumWidth(self.button_width)
        self.setMaximumWidth(self.button_max_width)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet(f"""
            QPushButton {{
                color: {FlameColors.TEXT_PRIMARY};
                background-color: {FlameColors.BG_WIDGET};
                border: none;
                font: 14px "Discreet";
                padding-left: 6px;
                text-align: left}}
            QPushButton:hover {{
                border: 1px solid {FlameColors.BORDER_HOVER}}}
            QPushButton:disabled {{
                color: {FlameColors.TEXT_SECONDARY};
                background-color: {FlameColors.BG_WIDGET};
                border: none}}
            QToolTip {{
                color: {FlameColors.TEXT_TOOLTIP};
                background-color: {FlameColors.BG_MEDIUM};
                border: 10px solid {FlameColors.BG_MEDIUM}}}""")

    def _insert_token(self, token: str) -> None:
        """Insert token value into token_dest LineEdit.

        If token is found in token_dict, inserts the corresponding value
        into token_dest at the current cursor position.

        Args:
            token: Token name (key) to look up in self.token_dict.

        Raises:
            AttributeError: If token_dest has been deleted or is invalid.
            RuntimeError: If token_dest.insert() fails due to runtime error.
        """
        if token in self.token_dict:
            try:
                self.token_dest.insert(self.token_dict[token])
            except AttributeError as error:
                raise AttributeError(
                    f'Cannot insert token "{token}": token_dest LineEdit widget '
                    'has been deleted or is invalid') from error
            except RuntimeError as error:
                raise RuntimeError(
                    f'Cannot insert token "{token}": token_dest.insert() '
                    'failed due to runtime error') from error

    def populate_menu(self, token_dict: dict[str, str]) -> None:
        """Populate the dropdown menu with tokens from token_dict.

        Creates a new menu widget and adds menu actions for each token in
        token_dict. Each action, when triggered, inserts the corresponding
        token_value into token_dest at the current cursor position.

        If self.sort is True, tokens are sorted case-insensitively first,
        then by case (lowercase precedes uppercase). If False, tokens
        maintain the dictionary's insertion order (Python 3.7+).

        Args:
            token_dict: Dictionary mapping token display names to token
                values. Keys are the names shown in the menu, values are
                the tokens inserted into the LineEdit. Format: {'Display
                Name': '<Token>'}. Can be empty (menu will have no items).
                Must have string keys and values if non-empty.

        Raises:
            TypeError: If token_dict keys or values are not strings.

        Note:
            This method replaces any existing menu. The token_dict is
            stored in self.token_dict and used for future token lookups.
            A parameter is used instead of self.token_dict to allow
            updating the menu with a new dictionary (e.g., from a setter).
        """
        self._check_token_dict(token_dict)
        self.token_dict = token_dict
        self.token_menu = QtWidgets.QMenu(self)
        self.token_menu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.token_menu.setStyleSheet(f"""
            QMenu {{
                color: {FlameColors.TEXT_PRIMARY};
                background-color: {FlameColors.BG_WIDGET};
                border: none;
                font: 14px "Discreet"}}
            QMenu::item:selected {{
                color: {FlameColors.TEXT_SELECTED};
                background-color: {FlameColors.BG_SELECTED}}}""")
        self.setMenu(self.token_menu)

        if self.sort:
            tokens = sorted(self.token_dict.items(), key=self._get_token_names_sorted)
            for name, _token in tokens:
                self.token_menu.addAction(name, partial(self._insert_token, name))
        else:
            for name, _token in self.token_dict.items():
                self.token_menu.addAction(name, partial(self._insert_token, name))
