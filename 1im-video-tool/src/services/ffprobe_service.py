import json
import subprocess
from pathlib import Path

from src.models.media_info import AudioStream, MediaInfo, VideoStream
from src.utils.resource_path import resource_path


class FFprobeError(RuntimeError):
    pass


def ffprobe_path() -> Path:
    return resource_path("bin", "ffprobe.exe")


def ffprobe_available() -> bool:
    return ffprobe_path().exists()


def parse_fps(value: str | None) -> float:
    if not value or value == "0/0" or "/" not in value:
        return 0.0
    numerator, denominator = value.split("/", 1)
    denominator_float = float(denominator)
    if denominator_float == 0:
        return 0.0
    return float(numerator) / denominator_float


def inspect_media(path: Path) -> MediaInfo:
    executable = ffprobe_path()
    if not executable.exists():
        raise FFprobeError("FFprobe를 찾을 수 없습니다.")
    command = [
        str(executable),
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    if completed.returncode != 0:
        raise FFprobeError("파일을 읽을 수 없거나 손상되었습니다.")
    data = json.loads(completed.stdout)
    duration = float(data.get("format", {}).get("duration") or 0)
    video = None
    audio = None
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and video is None:
            video = VideoStream(
                codec=stream.get("codec_name", ""),
                width=int(stream.get("width") or 0),
                height=int(stream.get("height") or 0),
                fps=parse_fps(stream.get("avg_frame_rate") or stream.get("r_frame_rate")),
                pix_fmt=stream.get("pix_fmt"),
            )
        if stream.get("codec_type") == "audio" and audio is None:
            audio = AudioStream(
                codec=stream.get("codec_name", ""),
                sample_rate=int(stream["sample_rate"]) if stream.get("sample_rate") else None,
                channels=int(stream["channels"]) if stream.get("channels") else None,
            )
    if duration <= 0:
        raise FFprobeError("영상 길이를 확인할 수 없습니다.")
    return MediaInfo(path=path, duration=duration, video=video, audio=audio)
