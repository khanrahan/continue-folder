"""Tests for token types used in input and output patterns."""

from continue_folder_token import (
    InputToken,
    InputTokenMax,
    Token,
    TokenIncrement,
    TokenPadded,
)


def test_token_replaces_bracket_pattern() -> None:
    assert Token('Day', 'DD', '17').resolve('shot_[DD]') == 'shot_17'


def test_token_replaces_every_occurrence() -> None:
    assert Token('Day', 'DD', '17').resolve('[DD]_[DD]') == '17_17'


def test_token_missing_value_is_empty() -> None:
    assert Token('Day', 'DD', None).resolve('[DD]') == ''


def test_token_string_uses_square_brackets() -> None:
    assert Token('Day', 'DD', '17').token == '[DD]'


def test_padded_token_uses_hashes() -> None:
    assert TokenPadded('Version', 'version', '4').resolve('[version###]') == (
        '004'
    )


def test_padded_token_without_hashes_is_unpadded() -> None:
    assert TokenPadded('Version', 'version', '4').resolve('[version]') == '4'


def test_increment_with_value() -> None:
    assert TokenIncrement('Version', 'version', '3').resolve('[version]') == (
        '4'
    )


def test_increment_with_no_value_starts_at_1() -> None:
    assert TokenIncrement('Version', 'version', None).resolve('[version]') == (
        '1'
    )


def test_increment_with_padding() -> None:
    assert TokenIncrement('Version', 'version', '9').resolve(
        '[version###]'
    ) == '010'


def test_input_token_consider_last_write_wins() -> None:
    token = InputToken('Year', 'YYYY', r'[0-9]{4}')
    token.consider('2024')
    token.consider('2026')
    assert token.value == '2026'


def test_input_token_max_keeps_highest() -> None:
    token = InputTokenMax('Version', 'version', r'[0-9]+')
    token.consider('2')
    token.consider('10')
    token.consider('abc')
    assert token.value == '10'


def test_input_token_max_ignores_only_non_digits() -> None:
    token = InputTokenMax('Version', 'version', r'[0-9]+')
    token.consider('abc')
    assert token.value is None


def test_input_token_string_uses_curly_braces() -> None:
    assert InputToken('Version', 'version', r'[0-9]+').token == '{version}'


def test_input_token_named_regex() -> None:
    token = InputToken('Version', 'version', r'[0-9]+')
    assert token.named_regex == r'(?P<version>[0-9]+)'
