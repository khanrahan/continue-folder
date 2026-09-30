"""Token types for Continue Folder patterns."""

import re
from dataclasses import dataclass


@dataclass
class Token:
    """Output token delimited with square brackets form the new result name.

    Attributes:
        name: Display name for the Add Token menu.
        pattern: Token excluding the square bracket delimiters.
        value: Stored capture, or the resolved value to emit for date tokens.
    """

    name: str
    pattern: str
    value: str | None

    @property
    def token(self) -> str:
        """Get token string."""
        return f'[{self.pattern}]'

    @property
    def regex(self) -> str:
        """Get regex string."""
        return rf'\[{self.pattern}\]'


@dataclass
class TokenPadded(Token):
    """Output token with optional padding modifier."""

    @property
    def next_value(self) -> str:
        """Return stored value plus one, or 1 when value is not a number."""
        n = int(self.value) if str(self.value).isdigit() else 0
        return str(n + 1)

    def process_match(self, match: re.Match) -> str:
        """Process a regex match and return the padded next value."""
        return self.next_value.zfill(len(match.group(1)))

    @property
    def regex(self) -> str:
        """Get regex string."""
        # capture the padding as a match group
        return rf'\[{self.pattern}(#*)\]'


@dataclass
class InputToken:
    """Input token delimited with curly braces.

    Used with a InputTokenStore to store sections of a common string pattern.

    Attributes:
        name: Display name for the Add Token menu.
        pattern: Token excluding the curly-brace delimiters (e.g. version).
        regex: Capture regex used when scanning folder names.
        value: Result after considering
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
