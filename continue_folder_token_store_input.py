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
        """Populate curly-brace input tokens for matching and capture."""
        self.tokens['am/pm'] = InputToken('pp', '[a-z]{2}')
        self.tokens['AM/PM'] = InputToken('PP', '[A-Z]{2}')
        self.tokens['Day'] = InputToken('DD', '[0-9]{2}')
        self.tokens['Hour (12hr)'] = InputToken('hh', '[0-9]{2}')
        self.tokens['Hour (24hr)'] = InputToken('HH', '[0-9]{2}')
        self.tokens['Minute'] = InputToken('mm', '[0-9]{2}')
        self.tokens['Month'] = InputToken('MM', '[0-9]{2}')
        self.tokens['Version'] = InputToken('version', '[0-9]*')
        self.tokens['Year (##)'] = InputToken('YY', '[0-9]{2}')
        self.tokens['Year (####)'] = InputToken('YYYY', '[0-9]{4}')

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
        """Fill the token values."""
        if self.folders:
            match = self.folders[-1][1]  # last folder's captured values
            for key, value in match.items():
                for token in self.tokens.values():
                    if key == token.pattern:
                        token.value = value

    def apply(self, pattern: str) -> None:
        """Scan destination with pattern and derive input token values."""
        self.pattern_regex = self.build_pattern_regex(pattern)
        self.find_folders(self.pattern_regex)
        self.fill_values()

    @property
    def name_token_pairs(self) -> dict[str, str]:
        """Map display names to insertable curly-brace patterns."""
        return {name: token.pattern for name, token in self.tokens.items()}

    @property
    def captured_token_values(self) -> dict[str, str]:
        """Map display names to captured values from destination folders."""
        return {name: token.value for name, token in self.tokens.items()}
