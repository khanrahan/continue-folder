"""Button Mixin Module.

This module provides the ButtonMixin class for button dimension validation.
"""


class ButtonMixin:
    """Mixin class providing button dimension validation.

    Provides a shared method for validating button width and max width
    parameters used by multiple button widget classes.
    """

    def _check_button_dimensions(
            self, button_width: int, button_max_width: int) -> None:
        """Validate button dimension parameters.

        Args:
            button_width: Minimum button width to validate.
            button_max_width: Maximum button width to validate.

        Raises:
            ValueError: If dimensions are invalid (non-positive or
                max_width < width).
        """
        if button_width <= 0:
            raise ValueError(
                f'button_width must be positive, got {button_width}')
        if button_max_width <= 0:
            raise ValueError(
                f'button_max_width must be positive, got {button_max_width}')
        if button_max_width < button_width:
            raise ValueError(
                f'button_max_width ({button_max_width}) must be >= '
                f'button_width ({button_width})')
