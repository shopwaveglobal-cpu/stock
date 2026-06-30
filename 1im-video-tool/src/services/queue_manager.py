import threading
from collections.abc import Callable

from src.models.job import Job, JobResult, JobStatus
from src.services.ffmpeg_runner import run_command_sequence, run_ffmpeg


ProgressCallback = Callable[[dict], None]


class QueueManager:
    def __init__(self, on_event: ProgressCallback) -> None:
        self.on_event = on_event
        self._cancel_current = threading.Event()
        self._stop_all = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, jobs: list[Job]) -> None:
        if self.is_running:
            raise RuntimeError("이미 작업이 실행 중입니다.")
        self._cancel_current.clear()
        self._stop_all.clear()
        self._thread = threading.Thread(target=self._run, args=(jobs,), daemon=True)
        self._thread.start()

    def cancel_current(self) -> None:
        self._cancel_current.set()

    def stop_all(self) -> None:
        self._stop_all.set()
        self._cancel_current.set()

    def _run(self, jobs: list[Job]) -> None:
        results: list[JobResult] = []
        total = len(jobs)
        for index, job in enumerate(jobs, start=1):
            if self._stop_all.is_set():
                break
            self._cancel_current.clear()
            self.on_event({"type": "job_start", "index": index, "total": total, "job": job})
            try:
                command_or_commands = job.command_factory()
                if command_or_commands and isinstance(command_or_commands[0], list):
                    run_command_sequence(command_or_commands, job.duration, self._progress_event, self._cancel_current.is_set)  # type: ignore[arg-type]
                else:
                    run_ffmpeg(command_or_commands, job.duration, self._progress_event, self._cancel_current.is_set)  # type: ignore[arg-type]
                result = JobResult(job.source, job.output, JobStatus.SUCCESS, "완료")
            except Exception as exc:
                status = JobStatus.CANCELED if self._cancel_current.is_set() else JobStatus.FAILED
                result = JobResult(job.source, job.output, status, str(exc))
            results.append(result)
            self.on_event({"type": "job_done", "result": result})
        self.on_event({"type": "queue_done", "results": results})

    def _progress_event(self, progress: float) -> None:
        self.on_event({"type": "progress", "progress": progress})
