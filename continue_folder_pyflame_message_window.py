"""PyFlame Message Window Widget Module.

This module provides the PyFlameMessageWindow widget class for creating
Flame-themed message dialog windows.
"""


from PySide6 import QtCore, QtGui, QtWidgets

from continue_folder_pyflame_button import PyFlameButton
from continue_folder_pyflame_colors import PyFlameColors
from continue_folder_pyflame_label import PyFlameLabel
from continue_folder_window_mixin import WindowMixin


class PyFlameMessageWindow(WindowMixin, QtWidgets.QDialog):
    """Custom PyFlame Message Window Widget.

    A custom dialog window with Flame-style theming that displays a message
    to the user. The window can be used to show informational messages, errors,
    warnings, or confirmation dialogs. The window type determines which buttons
    are shown and the color of the side bar. The window is frameless and can
    be dragged by clicking and dragging anywhere on the window.

    Examples:
        Error message:
            >>> PyFlameMessageWindow.error('An error occurred', parent)

        Confirmation dialog:
            >>> if PyFlameMessageWindow.confirm(
            ...     'Confirm Operation',
            ...     'Are you sure you want to proceed?', parent):
            ...     print('User confirmed')

        Warning dialog:
            >>> if PyFlameMessageWindow.warning(
            ...     'Warning', 'This operation cannot be undone', parent):
            ...     proceed_with_operation()

        Informational message:
            >>> PyFlameMessageWindow(
            ...     'Information', 'message',
            ...     'Operation completed successfully', parent).exec()

    Note:
        The window is modal and blocks interaction with other windows until
        closed. exec() returns QDialog.Accepted when the user clicks Confirm
        or Ok, and QDialog.Rejected when the user clicks Cancel or presses
        Escape.
    """

    # Side bar color constants
    _BLUE = QtGui.QColor(0, 110, 176)
    _GREY = QtGui.QColor(71, 71, 71)
    _RED = QtGui.QColor(200, 29, 29)
    _YELLOW_GOLD = QtGui.QColor(200, 172, 30)

    # Type hints for instance attributes
    _start_position: QtCore.QPoint
    cancel_button: PyFlameButton | None
    confirm_button: PyFlameButton | None
    grid: QtWidgets.QGridLayout
    main_label: PyFlameLabel
    message_text_edit: QtWidgets.QTextEdit
    message_type: str
    ok_button: PyFlameButton | None

    def __init__(
            self,
            message_title: str,
            message_type: str,
            message: str,
            parent: QtWidgets.QWidget | None = None
    ) -> None:
        """Initialize the PyFlameMessageWindow instance.

        Validates all parameters, stores instance variables, and initializes
        the window properties, UI widgets, and layout. The window is centered
        on the primary screen but not shown; call exec() to run it, or use
        one of the confirm(), warning(), or error() class methods.

        Args:
            message_title: Text displayed in the top left of the window. Must
                be a non-empty string.
            message_type: Type of message window. Must be one of: 'confirm',
                'message', 'error', or 'warning'. Determines which buttons
                are shown and the color of the side bar. 'confirm' and
                'warning' types show Confirm/Cancel buttons. 'message' and
                'error' types show an Ok button.
            message: Text to display in the message body of the window. Can
                be an empty string. HTML tags like '<br>', '<center>', and
                '<dd>' are automatically stripped.
            parent: Optional parent widget for the message window. If
                provided, the window will be a child of this widget.

        Raises:
            TypeError: If message_title, message_type, or message are not
                strings.
            ValueError: If message_title is empty, or message_type is not
                one of the allowed values.
        """
        super().__init__(parent)

        # Validate parameters
        self._check_message_title(message_title)
        self._check_message_type(message_type)
        self._check_message(message)

        # Side bar color mapping for message types
        self._side_bar_colors = {
            'confirm': PyFlameMessageWindow._GREY,
            'error': PyFlameMessageWindow._YELLOW_GOLD,
            'message': PyFlameMessageWindow._BLUE,
            'warning': PyFlameMessageWindow._RED,
        }

        # Store instance variables
        self.message_type = message_type

        # Initialize window properties
        self._init_window_properties()

        # Initialize widgets
        self._init_widgets(message_title, message_type, message)

        # Initialize layout
        self._init_layout(message_type)

        self._center_window()

    @classmethod
    def confirm(
            cls,
            title: str,
            message: str,
            parent: QtWidgets.QWidget | None = None,
    ) -> bool:
        """Show a Confirm/Cancel dialog and return True if confirmed."""
        dialog = cls(title, 'confirm', message, parent)
        return dialog.exec() == QtWidgets.QDialog.Accepted

    @classmethod
    def warning(
            cls,
            title: str,
            message: str,
            parent: QtWidgets.QWidget | None = None,
    ) -> bool:
        """Show a red Confirm/Cancel dialog and return True if confirmed."""
        dialog = cls(title, 'warning', message, parent)
        return dialog.exec() == QtWidgets.QDialog.Accepted

    @classmethod
    def error(
            cls,
            message: str,
            parent: QtWidgets.QWidget | None = None,
            title: str = 'Error',
    ) -> None:
        """Show an error dialog with an Ok button."""
        cls(title, 'error', message, parent).exec()

    def _init_widgets(
            self,
            message_title: str,
            message_type: str,
            message: str
    ) -> None:
        """Initialize UI widgets.

        Args:
            message_title: Text to display in the main label.
            message_type: Type of message window ('confirm', 'warning',
                'message', or 'error').
            message: Text to display in the message text edit.
        """
        self.grid = QtWidgets.QGridLayout()

        self.main_label = PyFlameLabel(message_title, 'normal', label_width=500)
        self.main_label.setStyleSheet(f"""
            color: {PyFlameColors.TEXT_PRIMARY};
            font: 18px 'Discreet'""")

        self.message_text_edit = QtWidgets.QTextEdit(message)
        self.message_text_edit.setDisabled(True)
        self.message_text_edit.setStyleSheet(WindowMixin._TEXT_EDIT_STYLESHEET)

        # Create buttons based on message type
        if message_type in ('confirm', 'warning'):
            self.confirm_button = PyFlameButton(
                'Confirm', self.accept, button_color='blue', button_width=110)
            self.cancel_button = PyFlameButton('Cancel', self.reject, button_width=110)
            self.ok_button = None
        else:
            self.ok_button = PyFlameButton(
                'Ok', self.accept, button_color='blue', button_width=110)
            self.confirm_button = None
            self.cancel_button = None

    def _init_window_properties(self) -> None:
        """Initialize window properties.

        Sets window flags, size, stylesheet, and modality.

        Notes:
            Setting WindowModality to ApplicationModal blocks all interaction
            with Flame until the dialog is closed.
        """
        self.setFixedSize(500, 330)
        self.setStyleSheet(f"""
            background-color: {PyFlameColors.BG_DARKER}""")
        self.setWindowFlags(
            QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)
        # Set window modality to application
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    def _init_layout(self, message_type: str) -> None:
        """Initialize layout.

        Adds all widgets to the grid layout and sets the layout on the
        window.

        Args:
            message_type: Type of message window ('confirm', 'warning',
                'message', or 'error'). Determines which buttons are added
                to the layout.
        """
        self.grid.addWidget(self.main_label, 0, 0)
        self.grid.setRowMinimumHeight(1, 30)
        self.grid.addWidget(self.message_text_edit, 2, 0, 4, 8)
        self.grid.setRowMinimumHeight(9, 30)

        if message_type in ('confirm', 'warning'):
            self.grid.addWidget(self.cancel_button, 10, 5)
            self.grid.addWidget(self.confirm_button, 10, 6)
        else:
            self.grid.addWidget(self.ok_button, 10, 6)

        self.grid.setRowMinimumHeight(11, 30)
        self.setLayout(self.grid)

    def _check_message_title(self, message_title: str) -> None:
        """Validate message_title parameter.

        Args:
            message_title: Window title to validate.

        Raises:
            TypeError: If message_title is not a string.
            ValueError: If message_title is empty.
        """
        if not isinstance(message_title, str):
            raise TypeError(
                f'message_title must be a string, got {type(message_title).__name__}')
        if not message_title:
            raise ValueError('message_title cannot be empty')

    def _check_message_type(self, message_type: str) -> None:
        """Validate message_type parameter.

        Args:
            message_type: Message type to validate.

        Raises:
            TypeError: If message_type is not a string.
            ValueError: If message_type is not one of the allowed values.
        """
        if not isinstance(message_type, str):
            raise TypeError(
                f'message_type must be a string, got {type(message_type).__name__}')
        if message_type not in ('confirm', 'message', 'error', 'warning'):
            raise ValueError(
                f'message_type must be one of: confirm, message, error, warning. '
                f'Got {message_type}')

    def _check_message(self, message: str) -> None:
        """Validate message parameter.

        Args:
            message: Message text to validate.

        Raises:
            TypeError: If message is not a string.
        """
        if not isinstance(message, str):
            raise TypeError(
                f'message must be a string, got {type(message).__name__}')

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """Handle paint events for custom window drawing.

        Draws the colored side bar and horizontal line below the title based
        on the message_type setting.

        Args:
            event: Paint event information from Qt.
        """
        painter = QtGui.QPainter(self)

        line_color = self._side_bar_colors.get(
            self.message_type, self._side_bar_colors['confirm'])

        painter.setPen(QtGui.QPen(line_color, 6, QtCore.Qt.SolidLine))
        painter.drawLine(0, 0, 0, 330)

        painter.setPen(QtGui.QPen(QtGui.QColor(71, 71, 71), .5, QtCore.Qt.SolidLine))
        painter.drawLine(0, 40, 500, 40)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """Handle mouse press events.

        Stores the initial mouse position when the mouse button is pressed.
        This is used to enable dragging the frameless window.

        Args:
            event: Mouse event information from Qt.
        """
        self._start_position = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """Handle mouse move event.

        Moves the window when the mouse is dragged while pressed. This
        enables dragging the frameless window by clicking and dragging
        anywhere on the window.

        Args:
            event: Mouse event information from Qt.

        Note:
            Silently handles AttributeError and RuntimeError exceptions
            that may occur if the window is being destroyed or if
            _start_position is not set.
        """
        try:
            delta = QtCore.QPoint(event.globalPos() - self._start_position)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._start_position = event.globalPos()
        except (AttributeError, RuntimeError):
            pass
