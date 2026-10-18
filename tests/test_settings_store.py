"""Tests for XML preset persistence."""

from pathlib import Path

import pytest

from continue_folder_destination import Destination
from continue_folder_preset import Preset
from continue_folder_settings_store import SettingsStore


def _store(path: Path) -> SettingsStore:
    return SettingsStore(path, 'Continue Folder', '3.0.0')


def _exports() -> Preset:
    return Preset(
        name='Exports',
        input_pattern='{YYYY}_v{version}',
        output_pattern='[YYYY]_v[version###]',
        destinations={Destination.REEL, Destination.FOLDER},
    )


def test_missing_file_starts_empty(tmp_path: Path) -> None:
    store = _store(tmp_path / 'settings.xml')
    assert store.preset_names == []
    assert store.presets == {}


def test_add_save_reload_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    store = _store(path)
    store.add_preset(_exports())
    store.save()

    reloaded = _store(path)
    preset = reloaded.presets['Exports']
    assert preset.input_pattern == '{YYYY}_v{version}'
    assert preset.output_pattern == '[YYYY]_v[version###]'
    assert preset.destinations == {Destination.REEL, Destination.FOLDER}


def test_corrupt_file_becomes_empty_store(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    path.write_text('not xml')
    store = _store(path)
    assert store.preset_names == []


def test_invalid_structure_becomes_empty_store(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    path.write_text('<settings></settings>')
    store = _store(path)
    assert store.preset_names == []


def test_add_empty_name_raises(tmp_path: Path) -> None:
    store = _store(tmp_path / 'settings.xml')
    with pytest.raises(ValueError, match='non-empty'):
        store.add_preset(Preset(name=''))


def test_delete_missing_preset_raises(tmp_path: Path) -> None:
    store = _store(tmp_path / 'settings.xml')
    with pytest.raises(ValueError, match='does not exist'):
        store.delete_preset(name='Nope')


def test_overwrite_preset(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    store = _store(path)
    store.add_preset(_exports())
    store.overwrite_preset(Preset(
        name='Exports',
        input_pattern='{version}',
        output_pattern='[version]',
        destinations={Destination.REEL},
    ))
    store.save()

    reloaded = _store(path)
    preset = reloaded.presets['Exports']
    assert preset.input_pattern == '{version}'
    assert preset.destinations == {Destination.REEL}


def test_overwrite_missing_preset_raises(tmp_path: Path) -> None:
    store = _store(tmp_path / 'settings.xml')
    with pytest.raises(ValueError, match='does not exist'):
        store.overwrite_preset(_exports())


def test_delete_preset(tmp_path: Path) -> None:
    store = _store(tmp_path / 'settings.xml')
    store.add_preset(_exports())
    store.delete_preset(name='Exports')
    assert store.preset_names == []


def test_sort_presets_is_case_sensitive(tmp_path: Path) -> None:
    store = _store(tmp_path / 'settings.xml')
    store.add_preset(Preset(name='alpha'))
    store.add_preset(Preset(name='Zulu'))
    store.sort_presets()
    assert store.preset_names == ['Zulu', 'alpha']


def test_nameless_presets_are_skipped(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    path.write_text(
        '<settings><script_name>Continue Folder'
        '<version>3.0.0<presets>'
        '<preset input_pattern="{version}"/>'
        '<preset name="Keep" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version></script_name></settings>'
    )
    store = _store(path)
    assert store.preset_names == ['Keep']
    assert set(store.presets) == {'Keep'}
