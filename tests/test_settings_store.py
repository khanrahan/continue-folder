"""Tests for XML preset persistence."""

import xml.etree.ElementTree as Etree
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


def test_previous_major_version_presets_are_ignored(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    path.write_text(
        '<settings><script_name>Continue Folder'
        '<version>2.0.0<presets>'
        '<preset name="Legacy" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version></script_name></settings>'
    )
    store = _store(path)
    assert store.preset_names == []

    store.add_preset(_exports())
    store.save()

    script = Etree.parse(path).find('script_name')
    versions = {
        element.text: [
            preset.get('name') for preset in element.find('presets')
        ]
        for element in script.findall('version')
    }
    assert versions['2.0.0'] == ['Legacy']
    assert versions['3.0.0'] == ['Exports']


def test_current_major_version_presets_are_used(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    path.write_text(
        '<settings><script_name>Continue Folder'
        '<version>2.0.0<presets>'
        '<preset name="Legacy" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version>'
        '<version>3.0.0<presets>'
        '<preset name="Current" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version>'
        '</script_name></settings>'
    )
    store = _store(path)
    assert store.preset_names == ['Current']


def test_same_major_version_presets_are_reused(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    path.write_text(
        '<settings><script_name>Continue Folder'
        '<version>3.0.0<presets>'
        '<preset name="Keep" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version></script_name></settings>'
    )
    store = SettingsStore(path, 'Continue Folder', '3.1.0')
    assert store.preset_names == ['Keep']


def test_highest_same_major_version_is_used(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    path.write_text(
        '<settings><script_name>Continue Folder'
        '<version>3.10.0<presets>'
        '<preset name="Highest" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version>'
        '<version>4.0.0<presets>'
        '<preset name="Newer Major" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version>'
        '<version>3.0.0<presets>'
        '<preset name="Oldest" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version>'
        '<version>3.9.2<presets>'
        '<preset name="Middle" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version>'
        '</script_name></settings>'
    )
    store = SettingsStore(path, 'Continue Folder', '3.1.0')
    assert store.preset_names == ['Highest']


def test_loaded_version_is_updated_to_running_version(tmp_path: Path) -> None:
    path = tmp_path / 'settings.xml'
    path.write_text(
        '<settings><script_name>Continue Folder'
        '<version>2.0.0<presets/></version>'
        '<version>3.0.1<presets>'
        '<preset name="Keep" input_pattern="{version}"'
        ' output_pattern="[version]" destinations="Desktop Reel"/>'
        '</presets></version></script_name></settings>'
    )
    store = SettingsStore(path, 'Continue Folder', '3.1.1')
    assert store.preset_names == ['Keep']
    store.save()

    script = Etree.parse(path).find('script_name')
    versions = [element.text for element in script.findall('version')]
    assert versions == ['2.0.0', '3.1.1']
