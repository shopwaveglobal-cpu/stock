from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoStream:
    codec: str
    width: int
    height: int
    fps: float
    pix_fmt: str | None = None


@dataclass(frozen=True)
class AudioStream:
    codec: str
    sample_rate: int | None = None
    channels: int | None = None


@dataclass(frozen=True)
class MediaInfo:
    path: Path
    duration: float
    video: VideoStream | None
    audio: AudioStream | None

    @property
    def has_audio(self) -> bool:
        return self.audio is not None
