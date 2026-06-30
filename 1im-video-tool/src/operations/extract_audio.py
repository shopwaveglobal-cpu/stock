from pathlib import Path

from src.models.media_info import MediaInfo
from src.operations.common import AUDIO_QUALITY, input_args, overwrite_output, progress_flags


AUDIO_EXTENSIONS = {
    "MP3": ".mp3",
    "M4A": ".m4a",
    "WAV": ".wav",
}


def build_extract_audio_command(info: MediaInfo, output: Path, audio_format: str = "MP3", quality: str = "일반") -> list[str]:
    if not info.has_audio:
        raise ValueError("오디오 트랙 없음")
    bitrate = AUDIO_QUALITY.get(quality, AUDIO_QUALITY["일반"])
    fmt = audio_format.upper()
    if fmt == "WAV":
        codec_args = ["-c:a", "pcm_s16le"]
    elif fmt == "M4A":
        codec_args = ["-c:a", "aac", "-b:a", bitrate]
    else:
        codec_args = ["-c:a", "libmp3lame", "-b:a", bitrate]
    return [
        *progress_flags(),
        *input_args(info.path),
        "-vn",
        *codec_args,
        *overwrite_output(output),
    ]
