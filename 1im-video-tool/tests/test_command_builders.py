from pathlib import Path

from src.models.media_info import AudioStream, MediaInfo, VideoStream
from src.operations.compress import build_compress_command
from src.operations.convert import build_convert_command
from src.operations.extract_audio import build_extract_audio_command
from src.operations.trim import build_trim_command


INFO = MediaInfo(
    path=Path("input.mov"),
    duration=100,
    video=VideoStream(codec="h264", width=1920, height=1080, fps=30),
    audio=AudioStream(codec="aac", sample_rate=48000, channels=2),
)


def test_convert_command_uses_transcoding_not_rename():
    command = build_convert_command(INFO, Path("out.mp4"), "mp4", "균형")
    assert "-c:v" in command
    assert "libx264" in command
    assert str(Path("out.mp4")) in command


def test_extract_audio_mp3_command_uses_audio_codec():
    command = build_extract_audio_command(INFO, Path("out.mp3"), "MP3", "일반")
    assert "-vn" in command
    assert "libmp3lame" in command


def test_trim_command_contains_start_and_duration():
    command = build_trim_command(INFO, Path("trim.mp4"), 2.5, 1.5)
    assert "-ss" in command
    assert "-t" in command
    assert "96.0" in command


def test_compress_command_calculates_bitrate():
    first_pass, second_pass, warning = build_compress_command(INFO, Path("small.mp4"), 25)
    assert first_pass is not None
    assert "-b:v" in second_pass
    assert warning is None
