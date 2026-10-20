"""Output token store for Continue Folder (square-bracket tokens)."""

import datetime as dt

from continue_folder_token import Token, TokenIncrement
from continue_folder_token_store_input import TokenStoreInput


class TokenStoreOutput:
    """Store tokens that form the new folder name.

    Square-bracket tokens ([DD], [YYYY], [version], …) are
    resolved into the output pattern. When a TokenStoreInput is provided,
    values such as version are read from it at resolve time. Optional hashes
    set zero-padding: [version###].
    """

    def __init__(self, token_store_input: TokenStoreInput | None = None) -> None:
        """Initialize output tokens.

        Args:
            token_store_input: Optional store used to supply derived values
                (e.g. version) when resolving the output pattern.
        """
        self.token_store_input = token_store_input
        self.tokens: dict[str, Token] = {}
        self._build_tokens()

    def _get_input_token_value(self, token_pattern: str) -> str | None:
        """Get the value of an input token by name."""
        if self.token_store_input is None:
            return None
        return self.token_store_input.captured_token_values[token_pattern]

    def _build_tokens(self) -> None:
        """Populate square-bracket output tokens keyed by pattern."""
        now = dt.datetime.now()
        tokens = [
            Token('am/pm', 'pp', now.strftime('%p').lower()),
            Token('AM/PM', 'PP', now.strftime('%p').upper()),
            Token('Day', 'DD', now.strftime('%d')),
            Token('Hour (12hr)', 'hh', now.strftime('%I')),
            Token('Hour (24hr)', 'HH', now.strftime('%H')),
            Token('Minute', 'mm', now.strftime('%M')),
            Token('Month', 'MM', now.strftime('%m')),
            TokenIncrement(
                'Version',
                'version',
                self._get_input_token_value('version'),
            ),
            Token('Year (YY)', 'YY', now.strftime('%y')),
            Token('Year (YYYY)', 'YYYY', now.strftime('%Y')),
        ]
        self.tokens = {token.pattern: token for token in tokens}

    def resolve(self, pattern: str) -> str:
        """Replace square-bracket tokens in pattern with values."""
        self._build_tokens()
        folder_new = pattern
        for token in self.tokens.values():
            folder_new = token.resolve(folder_new)
        return folder_new

    @property
    def name_token_pairs(self) -> dict[str, str]:
        """Map display names to insertable square-bracket patterns."""
        return {token.name: token.token for token in self.tokens.values()}
