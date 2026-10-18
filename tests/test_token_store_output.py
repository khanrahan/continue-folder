"""Tests for resolving output patterns into a new folder name."""

import datetime as dt
from pathlib import Path

from continue_folder_token_store_input import InputTokenStore
from continue_folder_token_store_output import OutputTokenStore


def test_resolve_continues_padded_version(tmp_path: Path) -> None:
    (tmp_path / '2025_08_v003').mkdir()
    inputs = InputTokenStore(str(tmp_path))
    inputs.apply('{YYYY}_{MM}_v{version}')
    outputs = OutputTokenStore(inputs)
    now = dt.datetime.now()
    expected = f'{now:%Y}_{now:%m}_v004'
    assert outputs.resolve('[YYYY]_[MM]_v[version###]') == expected


def test_resolve_unpadded_version(tmp_path: Path) -> None:
    (tmp_path / 'v003').mkdir()
    inputs = InputTokenStore(str(tmp_path))
    inputs.apply('v{version}')
    outputs = OutputTokenStore(inputs)
    assert outputs.resolve('[version]') == '4'


def test_resolve_starts_at_one_when_no_folders(tmp_path: Path) -> None:
    inputs = InputTokenStore(str(tmp_path))
    inputs.apply('{version}')
    outputs = OutputTokenStore(inputs)
    assert outputs.resolve('[version]') == '1'
    assert outputs.resolve('[version###]') == '001'


def test_resolve_leaves_non_token_text(tmp_path: Path) -> None:
    (tmp_path / '003').mkdir()
    inputs = InputTokenStore(str(tmp_path))
    inputs.apply('{version}')
    outputs = OutputTokenStore(inputs)
    assert outputs.resolve('shot_[version]_final') == 'shot_4_final'


def test_date_tokens_are_replaced(tmp_path: Path) -> None:
    outputs = OutputTokenStore(InputTokenStore(str(tmp_path)))
    result = outputs.resolve('[YYYY]-[MM]-[DD]')
    assert '[' not in result
    assert result == dt.datetime.now().strftime('%Y-%m-%d')


def test_name_token_pairs_use_display_names(tmp_path: Path) -> None:
    outputs = OutputTokenStore(InputTokenStore(str(tmp_path)))
    assert outputs.name_token_pairs['Version'] == '[version]'
    assert outputs.name_token_pairs['Year (YYYY)'] == '[YYYY]'
