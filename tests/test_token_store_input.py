"""Tests for scanning destination folders with input patterns."""

from pathlib import Path

from continue_folder_token_store_input import InputTokenStore


def _make_dirs(root: Path, names: list[str]) -> None:
    for name in names:
        (root / name).mkdir()


def test_literal_dot_is_not_a_wildcard(tmp_path: Path) -> None:
    _make_dirs(tmp_path, ['v1.003', 'v1X003'])
    store = InputTokenStore(str(tmp_path))
    store.apply('v1.{version}')
    assert [name for name, _ in store.folders] == ['v1.003']


def test_version_is_numeric_max(tmp_path: Path) -> None:
    _make_dirs(tmp_path, ['2026_08_v001', '2026_08_v003', '2026_08_v002'])
    (tmp_path / 'notes.txt').write_text('')
    store = InputTokenStore(str(tmp_path))
    store.apply('{YYYY}_{MM}_v{version}')
    assert store.captured_token_values['version'] == '3'
    assert store.captured_token_values['YYYY'] == '2026'
    assert store.captured_token_values['MM'] == '08'


def test_repeated_token_must_match_same_value(tmp_path: Path) -> None:
    _make_dirs(tmp_path, ['aa_aa', 'aa_bb'])
    store = InputTokenStore(str(tmp_path))
    store.apply('{pp}_{pp}')
    assert [name for name, _ in store.folders] == ['aa_aa']


def test_unknown_token_is_literal(tmp_path: Path) -> None:
    _make_dirs(tmp_path, ['{foo}_12', 'bar_12'])
    store = InputTokenStore(str(tmp_path))
    store.apply('{foo}_{version}')
    assert [name for name, _ in store.folders] == ['{foo}_12']


def test_missing_directory_returns_no_folders(tmp_path: Path) -> None:
    store = InputTokenStore(str(tmp_path / 'does_not_exist'))
    store.apply('{version}')
    assert store.folders == []
    assert store.captured_token_values['version'] is None


def test_date_token_last_write_wins_in_name_order(tmp_path: Path) -> None:
    _make_dirs(tmp_path, ['2025_shot', '2024_shot'])
    store = InputTokenStore(str(tmp_path))
    store.apply('{YYYY}_shot')
    assert store.captured_token_values['YYYY'] == '2025'


def test_non_matching_folders_are_ignored(tmp_path: Path) -> None:
    _make_dirs(tmp_path, ['001', 'not_a_version'])
    store = InputTokenStore(str(tmp_path))
    store.apply('{version}')
    assert [name for name, _ in store.folders] == ['001']


def test_name_token_pairs_use_display_names(tmp_path: Path) -> None:
    store = InputTokenStore(str(tmp_path))
    assert store.name_token_pairs['Version'] == '{version}'
    assert store.name_token_pairs['Year (YYYY)'] == '{YYYY}'
