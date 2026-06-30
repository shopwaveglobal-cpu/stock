import queue
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None

from src.models.job import Job, JobResult, JobStatus
from src.models.media_info import MediaInfo
from src.operations.compress import build_compress_command
from src.operations.convert import CONTAINER_EXTENSIONS, build_convert_command
from src.operations.extract_audio import AUDIO_EXTENSIONS, build_extract_audio_command
from src.operations.merge import build_compat_merge_command, build_fast_merge_command, can_fast_concat
from src.operations.trim import build_trim_command
from src.services.ffmpeg_runner import ffmpeg_available
from src.services.ffprobe_service import FFprobeError, ffprobe_available, inspect_media
from src.services.logger_service import write_queue_log
from src.services.path_service import default_output_dir, unique_output_path
from src.services.queue_manager import QueueManager
from src.ui.dialogs import confirm_low_quality, show_about, show_error, show_info
from src.ui.theme import ACCENT, BG, apply_theme
from src.utils.validation import is_inside_output_folder, is_supported_media, parse_seconds, parse_target_size_mb


FEATURES = {
    "convert": "영상 형식 바꾸기",
    "compress": "영상 용량 줄이기",
    "extract": "영상에서 음원 추출",
    "trim": "앞뒤 몇 초 자르기",
    "merge": "영상 이어붙이기",
}

FEATURE_OUTPUT_DIRS = {
    "convert": "형식변환",
    "compress": "용량줄이기",
    "extract": "음원추출",
    "trim": "자르기",
    "merge": "이어붙이기",
}


class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("1IM Video Tool")
        self.root.geometry("1080x760")
        self.root.minsize(960, 680)
        apply_theme(root)

        self.feature_var = tk.StringVar(value="convert")
        self.output_override = tk.StringVar(value="기본 위치")
        self.convert_format = tk.StringVar(value="mp4")
        self.convert_quality = tk.StringVar(value="균형")
        self.compress_target = tk.StringVar(value="100 MB")
        self.compress_custom = tk.StringVar(value="")
        self.audio_format = tk.StringVar(value="MP3")
        self.audio_quality = tk.StringVar(value="일반")
        self.trim_start = tk.StringVar(value="0")
        self.trim_end = tk.StringVar(value="0")
        self.merge_name = tk.StringVar(value="merged_video")
        self.merge_mode = tk.StringVar(value="auto")
        self.status_var = tk.StringVar(value="파일을 추가하세요.")
        self.current_var = tk.StringVar(value="현재 파일: -")
        self.count_var = tk.StringVar(value="선택된 파일 0개")

        self.media_infos: dict[Path, MediaInfo] = {}
        self.selected_files: list[Path] = []
        self.event_queue: queue.Queue[dict] = queue.Queue()
        self.queue_manager = QueueManager(self.event_queue.put)
        self.results: list[JobResult] = []
        self.last_output_folder: Path | None = None

        self._build()
        self._poll_events()
        self._refresh_settings()
        self._refresh_start_state()

    def _build(self) -> None:
        outer = ttk.Frame(self.root, padding=20)
        outer.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(2, weight=1)

        header = ttk.Frame(outer)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="1IM Video Tool", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="복잡한 영상 파일 작업을 폴더째 처리하는 도구", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Button(header, text="설정 / 정보", command=lambda: show_about(self.root)).grid(row=0, column=1, rowspan=2, sticky="e")

        nav = ttk.Frame(outer, style="Panel.TFrame", padding=12)
        nav.grid(row=1, column=0, rowspan=2, sticky="nsw", pady=(18, 0), padx=(0, 16))
        for index, (key, label) in enumerate(FEATURES.items()):
            ttk.Radiobutton(nav, text=label, value=key, variable=self.feature_var, command=self._on_feature_changed).grid(row=index, column=0, sticky="w", pady=5)

        controls = ttk.Frame(outer)
        controls.grid(row=1, column=1, sticky="ew", pady=(18, 8))
        for index, text in enumerate(("파일 추가", "폴더 추가", "선택 제거", "전체 비우기")):
            command = (self._add_files, self._add_folder, self._remove_selected, self._clear_files)[index]
            ttk.Button(controls, text=text, command=command).grid(row=0, column=index, padx=(0, 8))
        ttk.Label(controls, textvariable=self.count_var, style="Muted.TLabel").grid(row=0, column=4, sticky="w", padx=(10, 0))

        body = ttk.Frame(outer)
        body.grid(row=2, column=1, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        self.drop_label = ttk.Label(body, text="또는 파일을 여기로 끌어놓으세요", anchor="center", padding=12)
        self.drop_label.grid(row=0, column=0, sticky="ew")
        if TkinterDnD and DND_FILES:
            try:
                self.drop_label.drop_target_register(DND_FILES)
                self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
            except tk.TclError:
                self.drop_label.configure(text="Drag-and-drop을 초기화하지 못했습니다. 버튼으로 파일을 추가하세요.")
        else:
            self.drop_label.configure(text="Drag-and-drop은 tkinterdnd2 설치 후 사용할 수 있습니다.")

        columns = ("path", "duration", "audio")
        self.file_tree = ttk.Treeview(body, columns=columns, show="headings", selectmode="extended")
        self.file_tree.heading("path", text="선택된 파일 목록")
        self.file_tree.heading("duration", text="길이")
        self.file_tree.heading("audio", text="오디오")
        self.file_tree.column("path", width=620)
        self.file_tree.column("duration", width=90, anchor="center")
        self.file_tree.column("audio", width=90, anchor="center")
        self.file_tree.grid(row=1, column=0, sticky="nsew", pady=(8, 8))

        merge_buttons = ttk.Frame(body)
        merge_buttons.grid(row=2, column=0, sticky="ew")
        ttk.Button(merge_buttons, text="위로", command=lambda: self._move_selected(-1)).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(merge_buttons, text="아래로", command=lambda: self._move_selected(1)).grid(row=0, column=1, padx=(0, 6))

        self.settings_frame = ttk.Frame(body, style="Panel.TFrame", padding=14)
        self.settings_frame.grid(row=3, column=0, sticky="ew", pady=(10, 8))

        output_frame = ttk.Frame(body)
        output_frame.grid(row=4, column=0, sticky="ew")
        output_frame.columnconfigure(1, weight=1)
        ttk.Label(output_frame, text="저장 위치:").grid(row=0, column=0, sticky="w")
        ttk.Label(output_frame, textvariable=self.output_override, style="Muted.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 8))
        ttk.Button(output_frame, text="변경", command=self._choose_output_folder).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(output_frame, text="기본 위치", command=self._reset_output_folder).grid(row=0, column=3)

        action_frame = ttk.Frame(body)
        action_frame.grid(row=5, column=0, sticky="ew", pady=(14, 8))
        self.start_button = ttk.Button(action_frame, text="변환 시작", style="Accent.TButton", command=self._start)
        self.start_button.grid(row=0, column=0, padx=(0, 8))
        ttk.Button(action_frame, text="현재 작업 취소", command=self.queue_manager.cancel_current).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(action_frame, text="전체 작업 중지", command=self.queue_manager.stop_all).grid(row=0, column=2)

        progress_frame = ttk.Frame(body)
        progress_frame.grid(row=6, column=0, sticky="ew")
        progress_frame.columnconfigure(0, weight=1)
        ttk.Label(progress_frame, text="진행 상태").grid(row=0, column=0, sticky="w")
        ttk.Label(progress_frame, textvariable=self.status_var, style="Muted.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(progress_frame, textvariable=self.current_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w")
        self.progress = ttk.Progressbar(progress_frame, mode="determinate", maximum=100)
        self.progress.grid(row=3, column=0, sticky="ew", pady=(8, 0))

        result_columns = ("status", "source", "output")
        self.result_tree = ttk.Treeview(body, columns=result_columns, show="headings", height=5)
        self.result_tree.heading("status", text="결과")
        self.result_tree.heading("source", text="원본")
        self.result_tree.heading("output", text="출력")
        self.result_tree.column("status", width=90, anchor="center")
        self.result_tree.column("source", width=360)
        self.result_tree.column("output", width=420)
        self.result_tree.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(body, text="완료 후 폴더 열기", command=self._open_last_output).grid(row=8, column=0, sticky="e", pady=(8, 0))

    def _on_feature_changed(self) -> None:
        self._refresh_settings()
        self._refresh_start_state()

    def _refresh_settings(self) -> None:
        for child in self.settings_frame.winfo_children():
            child.destroy()
        feature = self.feature_var.get()
        if feature == "convert":
            self._combo_row("출력 형식", self.convert_format, ["mp4", "mov", "mkv"], 0)
            self._combo_row("품질", self.convert_quality, ["고화질", "균형", "작은 용량"], 1)
        elif feature == "compress":
            self._combo_row("목표 용량", self.compress_target, ["25 MB", "50 MB", "100 MB", "250 MB", "500 MB", "1 GB", "직접 입력"], 0)
            ttk.Label(self.settings_frame, text="직접 입력(MB)").grid(row=1, column=0, sticky="w", pady=4)
            ttk.Entry(self.settings_frame, textvariable=self.compress_custom, width=12).grid(row=1, column=1, sticky="w", pady=4)
            ttk.Label(self.settings_frame, text="영상 길이에 따라 비트레이트를 자동 조정합니다. 목표 크기와 실제 결과는 약간 다를 수 있습니다.", style="Muted.TLabel").grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        elif feature == "extract":
            self._combo_row("출력 형식", self.audio_format, ["MP3", "M4A", "WAV"], 0)
            self._combo_row("품질", self.audio_quality, ["고음질", "일반", "작은 용량"], 1)
        elif feature == "trim":
            ttk.Label(self.settings_frame, text="앞에서 제거").grid(row=0, column=0, sticky="w", pady=4)
            ttk.Entry(self.settings_frame, textvariable=self.trim_start, width=10).grid(row=0, column=1, sticky="w", pady=4)
            ttk.Label(self.settings_frame, text="초").grid(row=0, column=2, sticky="w", pady=4)
            ttk.Label(self.settings_frame, text="뒤에서 제거").grid(row=1, column=0, sticky="w", pady=4)
            ttk.Entry(self.settings_frame, textvariable=self.trim_end, width=10).grid(row=1, column=1, sticky="w", pady=4)
            ttk.Label(self.settings_frame, text="초").grid(row=1, column=2, sticky="w", pady=4)
        elif feature == "merge":
            ttk.Label(self.settings_frame, text="출력 파일명").grid(row=0, column=0, sticky="w", pady=4)
            ttk.Entry(self.settings_frame, textvariable=self.merge_name, width=28).grid(row=0, column=1, sticky="w", pady=4)
            self._combo_row("이어붙이기 방식", self.merge_mode, ["auto", "fast", "compat"], 1)

    def _combo_row(self, label: str, variable: tk.StringVar, values: list[str], row: int) -> None:
        ttk.Label(self.settings_frame, text=label).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Combobox(self.settings_frame, textvariable=variable, values=values, state="readonly", width=18).grid(row=row, column=1, sticky="w", pady=4)

    def _add_files(self) -> None:
        paths = filedialog.askopenfilenames(title="영상 파일 선택")
        self._add_paths([Path(path) for path in paths])

    def _add_folder(self) -> None:
        folder = filedialog.askdirectory(title="폴더 선택")
        if not folder:
            return
        paths = sorted([path for path in Path(folder).rglob("*") if path.is_file()])
        self._add_paths(paths)

    def _on_drop(self, event: object) -> None:
        data = getattr(event, "data", "")
        paths = [Path(item) for item in self.root.tk.splitlist(data)]
        expanded: list[Path] = []
        for path in paths:
            if path.is_dir():
                expanded.extend(sorted([child for child in path.rglob("*") if child.is_file()]))
            else:
                expanded.append(path)
        self._add_paths(expanded)

    def _add_paths(self, paths: list[Path]) -> None:
        if not ffprobe_available():
            show_error(self.root, "FFprobe를 찾을 수 없습니다. bin 폴더에 ffprobe.exe를 넣어주세요.")
            return
        added = 0
        for path in paths:
            path = path.resolve()
            if path in self.media_infos or not is_supported_media(path) or is_inside_output_folder(path):
                continue
            try:
                info = inspect_media(path)
            except FFprobeError as exc:
                self._insert_result(JobResult(path, None, JobStatus.FAILED, str(exc)))
                continue
            self.media_infos[path] = info
            self.selected_files.append(path)
            added += 1
        self._refresh_file_tree()
        self.status_var.set(f"{added}개 파일을 추가했습니다." if added else "추가할 수 있는 영상 파일이 없습니다.")
        self._refresh_start_state()

    def _refresh_file_tree(self) -> None:
        self.file_tree.delete(*self.file_tree.get_children())
        for path in self.selected_files:
            info = self.media_infos[path]
            duration = f"{info.duration:.1f}s"
            audio = "있음" if info.has_audio else "없음"
            self.file_tree.insert("", "end", iid=str(path), values=(str(path), duration, audio))
        self.count_var.set(f"선택된 파일 {len(self.selected_files)}개")

    def _remove_selected(self) -> None:
        selected = [Path(item) for item in self.file_tree.selection()]
        self.selected_files = [path for path in self.selected_files if path not in selected]
        for path in selected:
            self.media_infos.pop(path, None)
        self._refresh_file_tree()
        self._refresh_start_state()

    def _clear_files(self) -> None:
        self.selected_files.clear()
        self.media_infos.clear()
        self._refresh_file_tree()
        self._refresh_start_state()

    def _move_selected(self, direction: int) -> None:
        if self.feature_var.get() != "merge":
            return
        selection = self.file_tree.selection()
        if not selection:
            return
        path = Path(selection[0])
        index = self.selected_files.index(path)
        new_index = max(0, min(len(self.selected_files) - 1, index + direction))
        self.selected_files[index], self.selected_files[new_index] = self.selected_files[new_index], self.selected_files[index]
        self._refresh_file_tree()
        self.file_tree.selection_set(str(path))

    def _choose_output_folder(self) -> None:
        folder = filedialog.askdirectory(title="저장 위치 선택")
        if folder:
            self.output_override.set(folder)

    def _reset_output_folder(self) -> None:
        self.output_override.set("기본 위치")

    def _refresh_start_state(self) -> None:
        valid_count = len(self.selected_files)
        if self.feature_var.get() == "merge":
            enabled = valid_count >= 2 and not self.queue_manager.is_running
        else:
            enabled = valid_count >= 1 and not self.queue_manager.is_running
        self.start_button.configure(state="normal" if enabled else "disabled")

    def _output_dir_for(self, source: Path) -> Path:
        if self.output_override.get() != "기본 위치":
            return Path(self.output_override.get())
        return default_output_dir(source, FEATURE_OUTPUT_DIRS[self.feature_var.get()])

    def _start(self) -> None:
        if not ffmpeg_available():
            show_error(self.root, "FFmpeg를 찾을 수 없습니다. bin 폴더에 ffmpeg.exe를 넣어주세요.")
            return
        try:
            jobs = self._build_jobs()
        except ValueError as exc:
            show_error(self.root, str(exc))
            return
        if not jobs:
            show_error(self.root, "실행할 작업이 없습니다.")
            return
        self.results.clear()
        self.result_tree.delete(*self.result_tree.get_children())
        self.progress.configure(value=0)
        self.status_var.set("작업을 시작합니다.")
        self.queue_manager.start(jobs)
        self._refresh_start_state()

    def _build_jobs(self) -> list[Job]:
        feature = self.feature_var.get()
        if feature == "merge":
            return [self._build_merge_job()]
        jobs: list[Job] = []
        for path in self.selected_files:
            info = self.media_infos[path]
            output_dir = self._output_dir_for(path)
            output_dir.mkdir(parents=True, exist_ok=True)
            if feature == "convert":
                suffix = CONTAINER_EXTENSIONS[self.convert_format.get()]
                output = unique_output_path(output_dir, path.stem, suffix)
                jobs.append(Job(path, output, FEATURES[feature], info.duration, lambda info=info, output=output: build_convert_command(info, output, self.convert_format.get(), self.convert_quality.get())))
            elif feature == "compress":
                target = self.compress_custom.get() if self.compress_target.get() == "직접 입력" else self.compress_target.get()
                target_mb = parse_target_size_mb(target)
                output = unique_output_path(output_dir, f"{path.stem}_compressed", ".mp4")
                first, second, warning = build_compress_command(info, output, target_mb)
                if warning and not confirm_low_quality(self.root, warning):
                    continue
                jobs.append(Job(path, output, FEATURES[feature], info.duration, lambda first=first, second=second: [first, second]))
            elif feature == "extract":
                if not info.has_audio:
                    self._insert_result(JobResult(path, None, JobStatus.SKIPPED, "오디오 트랙 없음"))
                    continue
                suffix = AUDIO_EXTENSIONS[self.audio_format.get()]
                output = unique_output_path(output_dir, path.stem, suffix)
                jobs.append(Job(path, output, FEATURES[feature], info.duration, lambda info=info, output=output: build_extract_audio_command(info, output, self.audio_format.get(), self.audio_quality.get())))
            elif feature == "trim":
                start = parse_seconds(self.trim_start.get())
                end = parse_seconds(self.trim_end.get())
                output = unique_output_path(output_dir, f"{path.stem}_trimmed", ".mp4")
                jobs.append(Job(path, output, FEATURES[feature], info.duration, lambda info=info, output=output, start=start, end=end: build_trim_command(info, output, start, end)))
        return jobs

    def _build_merge_job(self) -> Job:
        infos = [self.media_infos[path] for path in self.selected_files]
        output_dir = self._output_dir_for(self.selected_files[0])
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = self.merge_name.get().strip() or "merged_video"
        output = unique_output_path(output_dir, safe_name, ".mp4")
        mode = self.merge_mode.get()
        duration = sum(info.duration for info in infos)

        def factory() -> list[str]:
            if mode == "fast" or (mode == "auto" and can_fast_concat(infos)):
                command, _ = build_fast_merge_command(infos, output)
                return command
            return build_compat_merge_command(infos, output)

        return Job(self.selected_files[0], output, FEATURES["merge"], duration, factory)

    def _poll_events(self) -> None:
        while True:
            try:
                event = self.event_queue.get_nowait()
            except queue.Empty:
                break
            self._handle_event(event)
        self.root.after(100, self._poll_events)

    def _handle_event(self, event: dict) -> None:
        event_type = event.get("type")
        if event_type == "job_start":
            job: Job = event["job"]
            self.status_var.set(f"전체 {event['index']} / {event['total']}")
            self.current_var.set(f"현재 파일: {job.source.name}")
        elif event_type == "progress":
            self.progress.configure(value=float(event["progress"]) * 100)
        elif event_type == "job_done":
            result: JobResult = event["result"]
            self.results.append(result)
            self._insert_result(result)
            if result.output:
                self.last_output_folder = result.output.parent
        elif event_type == "queue_done":
            results: list[JobResult] = event["results"]
            if results:
                first_output = next((result.output for result in results if result.output), None)
                if first_output:
                    self.last_output_folder = first_output.parent
                    write_queue_log(first_output.parent, self.feature_var.get(), results)
            self.progress.configure(value=100)
            self.status_var.set("작업이 완료되었습니다.")
            self.current_var.set("현재 파일: -")
            self._refresh_start_state()
            show_info(self.root, "작업이 완료되었습니다.")

    def _insert_result(self, result: JobResult) -> None:
        output = str(result.output) if result.output else "-"
        self.result_tree.insert("", "end", values=(result.status.value, str(result.source), output))

    def _open_last_output(self) -> None:
        if self.last_output_folder and self.last_output_folder.exists():
            subprocess.Popen(["explorer.exe", str(self.last_output_folder)])
        else:
            show_info(self.root, "아직 열 수 있는 출력 폴더가 없습니다.")


def main() -> None:
    root_cls = TkinterDnD.Tk if TkinterDnD else tk.Tk
    root = root_cls()
    MainWindow(root)
    root.mainloop()
