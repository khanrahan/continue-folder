"""Output token store for Continue Folder (square-bracket tokens)."""

from __future__ import annotations

import datetime as dt
import re
from typing import TYPE_CHECKING

from continue_folder_token import Token, TokenPadded

if TYPE_CHECKING:
    from continue_folder_token_store_input import InputTokenStore


class OutputTokenStore:
    """Store tokens that form the new folder name.

    Square-bracket tokens (``[DD]``, ``[YYYY]``, ``[version]``, …) are
    resolved into the output pattern. When an ``InputTokenStore`` is provided,
    values such as version are read from it at resolve time. Optional hashes
    set zero-padding: ``[version###]``.
    """

    def __init__(
            self,
            epoch: dt.datetime | None = None,
            input_token_store: InputTokenStore | None = None,
    ) -> None:
        """Initialize output tokens for ``epoch`` (default: now).

        Args:
            epoch: Datetime used for date/time output tokens.
            input_token_store: Optional store used to supply derived values
                (e.g. version) when resolving the output pattern.
        """
        self.now = epoch if epoch is not None else dt.datetime.now()
        self.input_token_store = input_token_store
        self.tokens: dict[str, Token] = {}
        self._build_tokens()

    def _build_tokens(self) -> None:
        """Populate square-bracket output tokens keyed by pattern."""
        tokens = [
            Token('am/pm', 'pp', self.now.strftime('%p').lower()),
            Token('AM/PM', 'PP', self.now.strftime('%p').upper()),
            Token('Day', 'DD', self.now.strftime('%d')),
            Token('Hour (12hr)', 'hh', self.now.strftime('%I')),
            Token('Hour (24hr)', 'HH', self.now.strftime('%H')),
            Token('Minute', 'mm', self.now.strftime('%M')),
            Token('Month', 'MM', self.now.strftime('%m')),
            TokenPadded(
                'Version',
                'version',
                self.input_token_store.captured_token_values['version'] or '0',
            ),
            Token('Year (YY)', 'YY', self.now.strftime('%y')),
            Token('Year (YYYY)', 'YYYY', self.now.strftime('%Y')),
        ]
        self.tokens = {token.pattern: token for token in tokens}

    def resolve(self, pattern: str) -> str:
        """Replace square-bracket tokens in pattern with values."""
        self._build_tokens()  # rebuild
        folder_new = pattern

        for token in self.tokens.values():
            if isinstance(token, TokenPadded):
                folder_new = re.sub(
                    token.regex,
                    token.process_match,
                    folder_new
                )
            else:
                folder_new = re.sub(
                    token.regex, token.value, folder_new
                )
        return folder_new

    @property
    def name_token_pairs(self) -> dict[str, str]:
        """Map display names to insertable square-bracket patterns."""
        return {token.name: token.token for token in self.tokens.values()}
