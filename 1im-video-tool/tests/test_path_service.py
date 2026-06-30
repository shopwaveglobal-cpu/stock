from pathlib import Path

from src.services.path_service import default_output_dir, unique_output_path


def test_default_output_dir_uses_source_parent_and_feature_name():
    result = default_output_dir(Path("D:/clips/a.mp4"), "변환")
    assert result == Path("D:/clips/1IM Video Tool Output/변환")


def test_unique_output_path_returns_base_when_available(tmp_path):
    target = unique_output_path(tmp_path, "clip", ".mp4")
    assert target == tmp_path / "clip.mp4"


def test_unique_output_path_adds_number_when_exists(tmp_path):
    (tmp_path / "clip.mp4").write_text("x", encoding="utf-8")
    target = unique_output_path(tmp_path, "clip", ".mp4")
    assert target == tmp_path / "clip_1.mp4"
