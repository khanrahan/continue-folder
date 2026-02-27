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
        """Populate square-bracket output tokens."""
        self.tokens['am/pm'] = Token('pp', self.now.strftime('%p').lower())
        self.tokens['AM/PM'] = Token('PP', self.now.strftime('%p').upper())
        self.tokens['Day'] = Token('DD', self.now.strftime('%d'))
        self.tokens['Hour (12hr)'] = Token('hh', self.now.strftime('%I'))
        self.tokens['Hour (24hr)'] = Token('HH', self.now.strftime('%H'))
        self.tokens['Minute'] = Token('mm', self.now.strftime('%M'))
        self.tokens['Month'] = Token('MM', self.now.strftime('%m'))
        self.tokens['Version'] = Token('version', '1')
        self.tokens['Year (YY)'] = Token('YY', self.now.strftime('%y'))
        self.tokens['Year (YYYY)'] = Token('YYYY', self.now.strftime('%Y'))
        self.tokens['Version'] = TokenPadded(
            'version',
            self.input_token_store.captured_token_values['Version'] or 1,
        )

    def resolve(self, pattern: str) -> str:
        """Replace square-bracket tokens in pattern with values."""
        self._build_tokens()  # rebuild
        folder_new = pattern

        for _, token in self.tokens.items():
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
        return {name: f'{token.token}' for name, token in self.tokens.items()}
