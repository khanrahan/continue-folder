"""Window Mixin Module.

This module provides the WindowMixin class for centering windows on the
primary screen.
"""

from continue_folder_flame_colors import FlameColors
from PySide6 import QtGui  # pylint: disable=import-error


class WindowMixin:
    """Mixin class providing window centering functionality.

    Provides a shared method for centering windows on the primary screen,
    used by multiple window/dialog widget classes.
    """

    _TEXT_EDIT_STYLESHEET = f"""
            QTextEdit {{
                color: {FlameColors.TEXT_PRIMARY};
                background-color: {FlameColors.BG_DARKER};
                selection-color: {FlameColors.TEXT_BRIGHT};
                selection-background-color: {FlameColors.BG_DARKER};
                border: none;
                padding-left: 20px;
                padding-right: 20px;
                font: 12px 'Discreet'}}"""

    def _center_window(self) -> None:
        """Center the window on the primary screen.

        Calculates the center position of the primary screen and moves the
        window to that position.

        Note:
            Important to note this is centering the window BEFORE it is shown.
            frameSize is based on setMinimumSize until the window is shown with
            show(), THEN it will reflect actual size.  Therefore, its important
            to have your setMinimumSize be very close to final size.
        """
        resolution = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))
