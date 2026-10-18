"""Tests for destination encode and decode."""

import pytest

from continue_folder_destination import Destination


@pytest.mark.parametrize(
    ('text', 'expected'),
    [
        ('', set()),
        ('Desktop Reel', {Destination.REEL}),
        (
            'Desktop Reel, MediaHub Folder',
            {Destination.REEL, Destination.FOLDER},
        ),
        ('Unknown, Desktop Reel', {Destination.REEL}),
        ('  MediaHub Folder  ', {Destination.FOLDER}),
    ],
)
def test_decode(text: str, expected: set[Destination]) -> None:
    assert Destination.decode(text) == expected


def test_encode_uses_definition_order() -> None:
    assert Destination.encode({Destination.FOLDER, Destination.REEL}) == (
        'Desktop Reel, MediaHub Folder'
    )


def test_encode_empty_set() -> None:
    assert Destination.encode(set()) == ''


def test_default_is_reel_only() -> None:
    assert Destination.default() == {Destination.REEL}


def test_encode_decode_roundtrip() -> None:
    destinations = {Destination.REEL, Destination.FOLDER}
    assert Destination.decode(Destination.encode(destinations)) == destinations
