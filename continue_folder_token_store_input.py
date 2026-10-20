"""Input token store for Continue Folder (curly-brace tokens)."""

import re
from pathlib import Path

from continue_folder_token import InputToken, InputTokenMax

TOKEN_REGEX = re.compile(r'\{(?P<pattern>\w+)\}')


class TokenStoreInput:
    """Store tokens that interpret destination folder names."""

    def __init__(self, path: str) -> None:
        """Initialize input tokens for destination path."""
        self.path = path
        self.tokens: dict[str, InputToken] = {}
        self.folders: list[tuple[str, dict[str, str]]] = []
        self.pattern_regex: re.Pattern[str] | None = None
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
            InputTokenMax('Version', 'version', '[0-9]+'),
            InputToken('Year (YY)', 'YY', '[0-9]{2}'),
            InputToken('Year (YYYY)', 'YYYY', '[0-9]{4}'),
        ]
        self.tokens = {token.pattern: token for token in tokens}

    def build_pattern_regex(self, pattern: str) -> re.Pattern[str]:
        """Translate an input pattern into a folder-matching regex.

        Text outside of recognized tokens is matched literally. A token
        repeated in the pattern must capture the same value each time.
        """
        regex_parts: list[str] = []
        found_patterns: set[str] = set()
        end_index = 0
        for token_match in TOKEN_REGEX.finditer(pattern):
            token = self.tokens.get(token_match['pattern'])
            if token is None:
                continue
            regex_parts.append(
                re.escape(pattern[end_index:token_match.start()]))
            if token.pattern in found_patterns:
                regex_parts.append(f'(?P={token.pattern})')
            else:
                regex_parts.append(token.named_regex)
                found_patterns.add(token.pattern)
            end_index = token_match.end()
        regex_parts.append(re.escape(pattern[end_index:]))
        return re.compile(''.join(regex_parts))

    def find_folders(
            self, pattern_regex: re.Pattern[str]
    ) -> list[tuple[str, dict[str, str]]]:
        """Return folders under self.path that fully match pattern_regex."""
        try:
            entries = list(Path(self.path).iterdir())
        except OSError:
            return []

        folders: list[tuple[str, dict[str, str]]] = []
        for entry in entries:
            if not entry.is_dir():
                continue
            match = pattern_regex.fullmatch(entry.name)
            if match:
                folders.append((match.group(0), match.groupdict()))
        return folders

    def fill_values(self) -> None:
        """Copy named groups from matching folders onto tokens.

        Last-wins tokens see captures in folder-name order. Max tokens
        consider every capture regardless of order.
        """
        for token in self.tokens.values():
            token.value = None
        for _, groups in sorted(self.folders, key=lambda folder: folder[0]):
            for key, captured in groups.items():
                if key in self.tokens:
                    self.tokens[key].consider(captured)

    def apply(self, pattern: str) -> None:
        """Scan destination with pattern and derive input token values."""
        self.pattern_regex = self.build_pattern_regex(pattern)
        self.folders = self.find_folders(self.pattern_regex)
        self.fill_values()

    @property
    def name_token_pairs(self) -> dict[str, str]:
        """Map display names to insertable curly-brace patterns."""
        return {token.name: token.token for token in self.tokens.values()}

    @property
    def captured_token_values(self) -> dict[str, str | None]:
        """Map token patterns to captured values from destination folders."""
        return {pattern: token.value for pattern, token in self.tokens.items()}
