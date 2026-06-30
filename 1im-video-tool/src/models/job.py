from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELED = "canceled"


@dataclass
class JobResult:
    source: Path
    output: Path | None
    status: JobStatus
    message: str


@dataclass
class Job:
    source: Path
    output: Path
    feature_name: str
    duration: float | None
    command_factory: Callable[[], list[str] | list[list[str]]]
    status: JobStatus = JobStatus.PENDING
    message: str = ""
    extra_outputs: list[Path] = field(default_factory=list)
