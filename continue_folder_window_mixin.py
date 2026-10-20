"""Window Mixin Module.

This module provides the WindowMixin class for centering windows on the
primary screen.
"""

from PySide6 import QtCore, QtGui

from continue_folder_pyflame_colors import PyFlameColors


class WindowMixin:
    """Mixin class providing window centering functionality.

    Provides a shared method for centering windows on the primary screen,
    used by multiple window/dialog widget classes.
    """

    _TEXT_EDIT_STYLESHEET = f"""
            QTextEdit {{
                color: {PyFlameColors.TEXT_PRIMARY};
                background-color: {PyFlameColors.BG_DARKER};
                selection-color: {PyFlameColors.TEXT_BRIGHT};
                selection-background-color: {PyFlameColors.BG_DARKER};
                border: none;
                padding-left: 20px;
                padding-right: 20px;
                font: 12px 'Discreet'}}"""

    _TITLE_BAR_HEIGHT = 28

    def _center_window(self) -> None:
        """Center the window on the primary screen.

        Calculates the center position of the primary screen and moves the
        window to that position.

        Note:
            Important to note this is centering the window BEFORE it is shown.
            Until then, the frame does not include the title bar, so the
            content area is positioned with setGeometry() and shifted down by
            half of an approximate _TITLE_BAR_HEIGHT for windows that are not
            frameless.  Title bars are about 28px on macOS and about 30-37px
            on Linux, depending on the window manager.  Positioning the frame
            with move() instead is unreliable on macOS, where dialogs with a
            parent or shown with exec() end up offset by a title bar height
            each.  The full screen geometry is used rather than the available
            geometry because Flame runs fullscreen.
        """
        self.adjustSize()
        rect = self.geometry()
        rect.moveCenter(
            QtGui.QGuiApplication.primaryScreen().geometry().center())
        if not self.windowFlags() & QtCore.Qt.FramelessWindowHint:
            rect.translate(0, self._TITLE_BAR_HEIGHT // 2)
        self.setGeometry(rect)
