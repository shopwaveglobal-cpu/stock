from pathlib import Path

import pytest

from src.utils.validation import (
    is_inside_output_folder,
    is_supported_media,
    parse_seconds,
    parse_target_size_mb,
    validate_trim_range,
)


def test_supported_media_extensions_are_case_insensitive():
    assert is_supported_media(Path("clip.MOV"))
    assert is_supported_media(Path("clip.mp4"))
    assert not is_supported_media(Path("notes.txt"))


def test_output_folder_detection_skips_recursive_outputs():
    path = Path("D:/video/1IM Video Tool Output/변환/clip.mp4")
    assert is_inside_output_folder(path)
    assert not is_inside_output_folder(Path("D:/video/clip.mp4"))


def test_parse_seconds_accepts_decimal_values():
    assert parse_seconds("1.5") == 1.5
    assert parse_seconds("0") == 0


def test_parse_seconds_rejects_negative_values():
    with pytest.raises(ValueError):
        parse_seconds("-1")


def test_parse_target_size_mb_accepts_presets_and_gb():
    assert parse_target_size_mb("25 MB") == 25
    assert parse_target_size_mb("1 GB") == 1024
    assert parse_target_size_mb("300") == 300


def test_trim_range_must_be_shorter_than_duration():
    validate_trim_range(1, 2, 10)
    with pytest.raises(ValueError):
        validate_trim_range(5, 5, 10)
