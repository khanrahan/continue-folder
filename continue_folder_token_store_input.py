"""Input token store for Continue Folder (curly-brace tokens)."""

from __future__ import annotations

import os
import re

from continue_folder_token import InputToken


class InputTokenStore:
    """Store tokens that interpret destination folder names."""

    def __init__(self, path: str) -> None:
        """Initialize input tokens for destination ``path``."""
        self.path = path
        self.tokens: dict[str, InputToken] = {}
        self.folders: list[dict] = []
        self.pattern_regex = ''
        self._build_tokens()

    def _build_tokens(self) -> None:
        """Populate curly-brace input tokens keyed by pattern."""
        tokens = [
            InputToken('am/pm', 'pp', '[a-z]{2}'),
            InputToken('AM/PM', 'PP', '[A-Z]{2}'),
            InputToken('Day', 'DD', '[0-9]{2}'),
            InputToken('Hour (12hr)', 'hh', '[0-9]{2}'),
            InputToken('Hour (24hr)', 'HH', '[0-9]{2}'),
            InputToken('Minute', 'mm', '[0-9]{2}'),
            InputToken('Month', 'MM', '[0-9]{2}'),
            InputToken('Version', 'version', '[0-9]*'),
            InputToken('Year (##)', 'YY', '[0-9]{2}'),
            InputToken('Year (####)', 'YYYY', '[0-9]{4}'),
        ]
        self.tokens = {token.pattern: token for token in tokens}

    @staticmethod
    def capture_tokens(regex: str, folder: str) -> re.Match | None:
        """Match folder against regex, returning None on error."""
        try:
            return re.match(regex, folder)
        except re.error:
            # e.g. duplicate named groups when {version} appears twice
            return None

    def build_pattern_regex(self, pattern: str) -> str:
        """Translate an input pattern into a folder-matching regex."""
        pattern_regex = pattern
        for token in self.tokens.values():
            pattern_regex = re.sub(
                re.escape(token.token), token.named_regex, pattern_regex
            )
        return pattern_regex

    def find_folders(self, pattern_regex: str) -> list[tuple]:
        """Return folders under self.path that match pattern_regex."""
        self.folders = []  # reset

        try:
            dirnames = next(os.walk(self.path))[1]
        except StopIteration:
            dirnames = []

        for folder in dirnames:
            search = self.capture_tokens(pattern_regex, folder)
            if not search:
                continue
            result = (search.group(0), search.groupdict())
            self.folders.append(result)
        self.folders.sort(key=lambda x: x[0])

    def fill_values(self) -> None:
        """Copy named groups from the last matching folder onto tokens."""
        if not self.folders:
            return
        match = self.folders[-1][1]
        for key, value in match.items():
            if key in self.tokens:
                self.tokens[key].value = value

    def apply(self, pattern: str) -> None:
        """Scan destination with pattern and derive input token values."""
        self.pattern_regex = self.build_pattern_regex(pattern)
        self.find_folders(self.pattern_regex)
        self.fill_values()

    @property
    def name_token_pairs(self) -> dict[str, str]:
        """Map display names to insertable curly-brace patterns."""
        return {token.name: token.token for token in self.tokens.values()}

    @property
    def captured_token_values(self) -> dict[str, str]:
        """Map token patterns to captured values from destination folders."""
        return {pattern: token.value for pattern, token in self.tokens.items()}
