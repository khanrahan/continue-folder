"""Tests for resolving output patterns into a new folder name."""

import datetime as dt
from pathlib import Path

from continue_folder_token_store_input import TokenStoreInput
from continue_folder_token_store_output import TokenStoreOutput


def test_resolve_continues_padded_version(tmp_path: Path) -> None:
    (tmp_path / '2025_08_v003').mkdir()
    inputs = TokenStoreInput(str(tmp_path))
    inputs.apply('{YYYY}_{MM}_v{version}')
    outputs = TokenStoreOutput(inputs)
    now = dt.datetime.now()
    expected = f'{now:%Y}_{now:%m}_v004'
    assert outputs.resolve('[YYYY]_[MM]_v[version###]') == expected


def test_resolve_unpadded_version(tmp_path: Path) -> None:
    (tmp_path / 'v003').mkdir()
    inputs = TokenStoreInput(str(tmp_path))
    inputs.apply('v{version}')
    outputs = TokenStoreOutput(inputs)
    assert outputs.resolve('[version]') == '4'


def test_resolve_starts_at_one_when_no_folders(tmp_path: Path) -> None:
    inputs = TokenStoreInput(str(tmp_path))
    inputs.apply('{version}')
    outputs = TokenStoreOutput(inputs)
    assert outputs.resolve('[version]') == '1'
    assert outputs.resolve('[version###]') == '001'


def test_resolve_leaves_non_token_text(tmp_path: Path) -> None:
    (tmp_path / '003').mkdir()
    inputs = TokenStoreInput(str(tmp_path))
    inputs.apply('{version}')
    outputs = TokenStoreOutput(inputs)
    assert outputs.resolve('shot_[version]_final') == 'shot_4_final'


def test_resolve_without_input_store_starts_at_one() -> None:
    outputs = TokenStoreOutput()
    assert outputs.resolve('[version##]') == '01'


def test_date_tokens_are_replaced() -> None:
    outputs = TokenStoreOutput()
    result = outputs.resolve('[YYYY]-[MM]-[DD]')
    assert '[' not in result
    assert result == dt.datetime.now().strftime('%Y-%m-%d')


def test_name_token_pairs_use_display_names() -> None:
    outputs = TokenStoreOutput()
    assert outputs.name_token_pairs['Version'] == '[version]'
    assert outputs.name_token_pairs['Year (YYYY)'] == '[YYYY]'
