"""Tests for preset defaults and XML conversion."""

from xml.etree.ElementTree import Element

from continue_folder_destination import Destination
from continue_folder_preset import (
    DEFAULT_INPUT_PATTERN,
    DEFAULT_OUTPUT_PATTERN,
    Preset,
)


def test_defaults() -> None:
    preset = Preset(name='Exports')
    assert preset.input_pattern == DEFAULT_INPUT_PATTERN
    assert preset.output_pattern == DEFAULT_OUTPUT_PATTERN
    assert preset.destinations == Destination.default()


def test_from_element_missing_attributes_use_defaults() -> None:
    preset = Preset.from_element(Element('preset', attrib={'name': 'Legacy'}))
    assert preset.name == 'Legacy'
    assert preset.input_pattern == DEFAULT_INPUT_PATTERN
    assert preset.output_pattern == DEFAULT_OUTPUT_PATTERN
    assert preset.destinations == Destination.default()


def test_from_element_empty_destinations_use_default() -> None:
    preset = Preset.from_element(Element('preset', attrib={
        'name': 'Empty',
        'destinations': '',
    }))
    assert preset.destinations == Destination.default()


def test_from_element_empty_patterns_use_defaults() -> None:
    preset = Preset.from_element(Element('preset', attrib={
        'name': 'Empty',
        'input_pattern': '',
        'output_pattern': '',
    }))
    assert preset.input_pattern == DEFAULT_INPUT_PATTERN
    assert preset.output_pattern == DEFAULT_OUTPUT_PATTERN


def test_to_element_from_element_roundtrip() -> None:
    original = Preset(
        name='Exports',
        input_pattern='{YYYY}_v{version}',
        output_pattern='[YYYY]_v[version###]',
        destinations={Destination.REEL, Destination.FOLDER},
    )
    restored = Preset.from_element(original.to_element())
    assert restored == original
