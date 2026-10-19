"""Token types for Continue Folder patterns."""

import re
from dataclasses import dataclass


@dataclass
class Token:
    """Output token to be replaced in a new folder name.

    Token delimited with square brackets that will be resolved to values when
    forming the new result name.

    Attributes:
        name: Display name for the Add Token menu.
        pattern: Token excluding the square bracket delimiters.
        input_value: Value the token is built from.
    """

    name: str
    pattern: str
    input_value: str | None

    @property
    def token(self) -> str:
        """Get token string."""
        return f'[{self.pattern}]'

    @property
    def value(self) -> str:
        """Value to emit in the new folder name."""
        return self.input_value or ''

    def resolve(self, text: str) -> str:
        """Return text with every occurrence of this token replaced."""
        return text.replace(self.token, self.value)


@dataclass
class TokenPadded(Token):
    """Output token with optional zero-padding, e.g. ``[frame####]``."""

    def resolve(self, text: str) -> str:
        """Return text with this token replaced and zero-padded per hash."""
        return re.sub(
            rf'\[{self.pattern}(?P<padding>#*)\]',
            lambda match: self.value.zfill(len(match['padding'])),
            text,
        )


@dataclass
class TokenIncrement(TokenPadded):
    """Padded output token whose value is one more than its input value."""

    @property
    def value(self) -> str:
        """Input value plus one, or 1 when there is no input value."""
        return str(int(self.input_value) + 1) if self.input_value else '1'


@dataclass
class InputToken:
    """Input token delimited with curly braces.

    Used with an InputTokenStore to store sections of a common string pattern.

    Attributes:
        name: Display name for the Add Token menu.
        pattern: Token excluding the curly-brace delimiters (e.g. version).
        regex: Capture regex used when scanning folder names.
        value: Result after considering all captures.
    """

    name: str
    pattern: str
    regex: str
    value: str | None = None  # filled after scan

    def consider(self, captured: str) -> None:
        """Consider a capture; last write wins."""
        self.value = captured

    @property
    def token(self) -> str:
        """Get token string."""
        return rf'{{{self.pattern}}}'

    @property
    def named_regex(self) -> str:
        """Get pattern named group regex."""
        return rf'(?P<{self.pattern}>{self.regex})'


@dataclass
class InputTokenMax(InputToken):
    """Input token that keeps the numeric max of all captures."""

    def consider(self, captured: str) -> None:
        """Keep the highest integer capture; ignore non-digits."""
        if not captured.isdigit():
            return
        number = int(captured)
        if self.value is None or number > int(self.value):
            self.value = str(number)
