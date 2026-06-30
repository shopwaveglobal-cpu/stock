from pathlib import Path

from src.models.media_info import MediaInfo
from src.operations.common import QUALITY_CRF, h264_aac_args, input_args, overwrite_output, progress_flags


CONTAINER_EXTENSIONS = {
    "mp4": ".mp4",
    "mov": ".mov",
    "mkv": ".mkv",
}


def build_convert_command(info: MediaInfo, output: Path, container: str = "mp4", quality: str = "균형") -> list[str]:
    crf = QUALITY_CRF.get(quality, QUALITY_CRF["균형"])
    return [
        *progress_flags(),
        *input_args(info.path),
        *h264_aac_args(crf=crf, audio=info.has_audio),
        *overwrite_output(output),
    ]
