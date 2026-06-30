from pathlib import Path

from src.models.media_info import MediaInfo
from src.operations.common import h264_aac_args, input_args, overwrite_output, progress_flags
from src.utils.validation import validate_trim_range


def build_trim_command(info: MediaInfo, output: Path, start_seconds: float, end_seconds: float) -> list[str]:
    validate_trim_range(start_seconds, end_seconds, info.duration)
    duration = info.duration - start_seconds - end_seconds
    return [
        *progress_flags(),
        "-ss",
        str(start_seconds),
        *input_args(info.path),
        "-t",
        str(duration),
        *h264_aac_args(crf=20, audio=info.has_audio),
        *overwrite_output(output),
    ]
