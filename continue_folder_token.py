"""Token types for Continue Folder patterns."""

import re
from dataclasses import dataclass


@dataclass
class Token:
    """Output token: square brackets form the new folder name.

    Attributes:
        name: Display name for the Add Token menu.
        pattern: Token excluding the square bracket delimiters.
        value: Resolved value to emit into the new folder name.
    """

    name: str
    pattern: str
    value: str

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
    """Output token with optional padding modifier.

    ``value`` is the stored capture (e.g. highest existing version).
    Emission uses ``next_value`` so the new folder continues the sequence.
    """

    @property
    def next_value(self) -> str:
        """Return stored value plus one, or ``1`` when value is not a number."""
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
    """Input token: curly braces interpret destination folder names.

    Attributes:
        name: Display name for the Add Token menu.
        pattern: Token excluding the curly-brace delimiters (e.g. version).
        regex: Capture regex used when scanning folder names.
        value: Result value after scanning (e.g. next version number).
    """

    name: str
    pattern: str
    regex: str
    value: str | None = None  # filled after scan

    @property
    def token(self) -> str:
        """Get token string."""
        return rf'{{{self.pattern}}}'

    @property
    def named_regex(self) -> str:
        """Get pattern named group regex."""
        return rf'(?P<{self.pattern}>{self.regex})'
