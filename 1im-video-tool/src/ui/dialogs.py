import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from src.services.ffmpeg_runner import ffmpeg_available, ffmpeg_path
from src.services.ffprobe_service import ffprobe_available, ffprobe_path
from src.utils.resource_path import resource_path


APP_VERSION = "1.0.0"


def show_about(parent: tk.Tk) -> None:
    status = (
        f"FFmpeg: {'감지됨' if ffmpeg_available() else '미탐지'} ({ffmpeg_path()})\n"
        f"FFprobe: {'감지됨' if ffprobe_available() else '미탐지'} ({ffprobe_path()})"
    )
    window = tk.Toplevel(parent)
    window.title("설정 / 정보")
    window.resizable(False, False)
    frame = ttk.Frame(window, padding=18)
    frame.grid(row=0, column=0, sticky="nsew")
    ttk.Label(frame, text="1IM Video Tool", font=("Malgun Gothic", 16, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(frame, text=f"버전 {APP_VERSION}").grid(row=1, column=0, sticky="w", pady=(6, 0))
    ttk.Label(frame, text=status, justify="left").grid(row=2, column=0, sticky="w", pady=(12, 0))
    ttk.Label(frame, text="모든 처리는 이 PC 안에서만 실행됩니다. 업로드, 계정, 분석 수집은 없습니다.", wraplength=460).grid(row=3, column=0, sticky="w", pady=(12, 0))
    ttk.Button(frame, text="Third-party notices 열기", command=open_notices).grid(row=4, column=0, sticky="w", pady=(14, 0))
    ttk.Button(frame, text="닫기", command=window.destroy).grid(row=5, column=0, sticky="e", pady=(14, 0))
    window.transient(parent)
    window.grab_set()


def open_notices() -> None:
    notices = resource_path("THIRD_PARTY_NOTICES.md")
    if notices.exists():
        subprocess.Popen(["notepad.exe", str(notices)])
    else:
        messagebox.showinfo("안내", "THIRD_PARTY_NOTICES.md 파일을 찾을 수 없습니다.")


def confirm_low_quality(parent: tk.Tk, warning: str) -> bool:
    return messagebox.askyesno("화질 경고", f"{warning}\n계속 진행할까요?", parent=parent)


def show_error(parent: tk.Tk, message: str) -> None:
    messagebox.showerror("오류", message, parent=parent)


def show_info(parent: tk.Tk, message: str) -> None:
    messagebox.showinfo("안내", message, parent=parent)
