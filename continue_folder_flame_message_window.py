"""Flame Message Window Widget Module.

This module provides the FlameMessageWindow widget class for creating
Flame-themed message dialog windows.
"""

from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets  # pylint: disable=import-error

from continue_folder_flame_button import FlameButton
from continue_folder_flame_colors import FlameColors
from continue_folder_flame_label import FlameLabel
from continue_folder_window_mixin import WindowMixin


class FlameMessageWindow(WindowMixin, QtWidgets.QDialog):
    """Custom Flame Message Window Widget.

    A custom dialog window with Flame-style theming that displays a message
    to the user. The window can be used to show informational messages, errors,
    warnings, or confirmation dialogs. The window type determines which buttons
    are shown and the color of the side bar. The window is frameless and can
    be dragged by clicking and dragging anywhere on the window.

    Examples:
        Error message:
            >>> FlameMessageWindow('Error', 'error', 'An error occurred')

        Confirmation dialog:
            >>> if FlameMessageWindow(
            ...     'Confirm Operation', 'confirm',
            ...     'Are you sure you want to proceed?'):
            ...     print('User confirmed')

        Warning dialog:
            >>> if FlameMessageWindow(
            ...     'Warning', 'warning',
            ...     'This operation cannot be undone'):
            ...     proceed_with_operation()

        Informational message:
            >>> FlameMessageWindow(
            ...     'Information', 'message',
            ...     'Operation completed successfully')

    Note:
        The window is modal and blocks interaction with other windows until
        closed. When used in a boolean context, 'confirm' and 'warning' types
        return True if the user clicked Confirm, False if Cancel. 'message'
        and 'error' types always return True.
    """

    # Side bar color constants
    _BLUE = QtGui.QColor(0, 110, 176)
    _GREY = QtGui.QColor(71, 71, 71)
    _RED = QtGui.QColor(200, 29, 29)
    _YELLOW_GOLD = QtGui.QColor(200, 172, 30)

    # Type hints for instance attributes
    _start_position: QtCore.QPoint
    cancel_button: Optional[FlameButton]
    confirm_button: Optional[FlameButton]
    confirmed: bool
    grid: QtWidgets.QGridLayout
    main_label: FlameLabel
    message_text_edit: QtWidgets.QTextEdit
    message_type: str
    ok_button: Optional[FlameButton]

    def __init__(
            self,
            message_title: str,
            message_type: str,
            message: str,
            parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        """Initialize the FlameMessageWindow instance.

        Validates all parameters, stores instance variables, and initializes
        the window properties, UI widgets, and layout. The window is
        automatically centered on the primary screen, shown, and executed as
        a modal dialog.

        Args:
            message_title: Text displayed in the top left of the window. Must
                be a non-empty string.
            message_type: Type of message window. Must be one of: 'confirm',
                'message', 'error', or 'warning'. Determines which buttons
                are shown and the color of the side bar. 'confirm' and
                'warning' types show Confirm/Cancel buttons and return True
                or False when used in a boolean context. 'message' and 'error'
                types show an Ok button.
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
        super().__init__()

        # Validate parameters
        self._check_message_title(message_title)
        self._check_message_type(message_type)
        self._check_message(message)

        # Side bar color mapping for message types
        self._side_bar_colors = {
            'confirm': FlameMessageWindow._GREY,
            'error': FlameMessageWindow._YELLOW_GOLD,
            'message': FlameMessageWindow._BLUE,
            'warning': FlameMessageWindow._RED,
        }

        # Store instance variables
        self.message_type = message_type
        self.confirmed = False

        # Initialize window properties
        self._init_window_properties(parent)

        # Initialize widgets
        self._init_widgets(message_title, message_type, message)

        # Initialize layout
        self._init_layout(message_type)

        # Show window
        self._center_window()
        self.show()
        self.raise_()
        self.activateWindow()
        self.exec()

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

        self.main_label = FlameLabel(message_title, 'normal', label_width=500)
        self.main_label.setStyleSheet(f"""
            color: {FlameColors.TEXT_PRIMARY};
            font: 18px 'Discreet'""")

        self.message_text_edit = QtWidgets.QTextEdit(message)
        self.message_text_edit.setDisabled(True)
        self.message_text_edit.setStyleSheet(WindowMixin._TEXT_EDIT_STYLESHEET)

        # Create buttons based on message type
        if message_type in ('confirm', 'warning'):
            self.confirm_button = FlameButton(
                'Confirm', self.confirm, button_color='blue', button_width=110)
            self.cancel_button = FlameButton('Cancel', self.cancel, button_width=110)
            self.ok_button = None
        else:
            self.ok_button = FlameButton(
                'Ok', self.confirm, button_color='blue', button_width=110)
            self.confirm_button = None
            self.cancel_button = None

    def _init_window_properties(
            self, parent: Optional[QtWidgets.QWidget]) -> None:
        """Initialize window properties.

        Sets window attributes, flags, size, stylesheet, and parent widget.

        Args:
            parent: Optional parent widget.

        Notes:
            Setting WindowModality to ApplicationModal blocks all interaction
            with Flame until the dialog is closed.
        """
        self.setMinimumSize(QtCore.QSize(500, 330))
        self.setMaximumSize(QtCore.QSize(500, 330))
        self.setStyleSheet(f"""
            background-color: {FlameColors.BG_DARKER}""")
        if parent:
            self.setParent(parent)
        # Set window flags after parent to ensure proper stacking
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

    def __bool__(self) -> bool:
        """Return the confirmation state of the dialog.

        Returns:
            Returns True if the user confirmed the dialog (clicked Confirm or
            Ok), False if cancelled (clicked Cancel or closed the dialog).
        """
        return self.confirmed

    def cancel(self) -> None:
        """Cancel the dialog.

        Closes the dialog window and sets the confirmed flag to False.
        """
        self.close()
        self.confirmed = False

    def confirm(self) -> None:
        """Confirm the dialog.

        Closes the dialog window and sets the confirmed flag to True.
        """
        self.close()
        self.confirmed = True

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # noqa: N802 pylint: disable=invalid-name,unused-argument
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

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:  # noqa: N802 pylint: disable=invalid-name
        """Handle mouse press events.

        Stores the initial mouse position when the mouse button is pressed.
        This is used to enable dragging the frameless window.

        Args:
            event: Mouse event information from Qt.
        """
        self._start_position = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:  # noqa: N802 pylint: disable=invalid-name
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
