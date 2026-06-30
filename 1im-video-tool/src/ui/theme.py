import tkinter as tk
from tkinter import ttk


BG = "#181818"
PANEL = "#242424"
FIELD = "#303030"
FG = "#F5F5F5"
MUTED = "#B8B8B8"
ACCENT = "#F37021"


def apply_theme(root: tk.Tk) -> None:
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=BG, foreground=FG, fieldbackground=FIELD, bordercolor=PANEL, lightcolor=PANEL, darkcolor=PANEL)
    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED)
    style.configure("Title.TLabel", background=BG, foreground=FG, font=("Malgun Gothic", 22, "bold"))
    style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Malgun Gothic", 10))
    style.configure("TButton", background=FIELD, foreground=FG, padding=(10, 7), font=("Malgun Gothic", 10))
    style.map("TButton", background=[("active", ACCENT), ("disabled", "#333333")], foreground=[("disabled", "#777777")])
    style.configure("Accent.TButton", background=ACCENT, foreground="#111111", font=("Malgun Gothic", 10, "bold"))
    style.map("Accent.TButton", background=[("active", "#ff8a3d"), ("disabled", "#55311f")])
    style.configure("TEntry", fieldbackground=FIELD, foreground=FG, insertcolor=FG)
    style.configure("TCombobox", fieldbackground=FIELD, foreground=FG, arrowcolor=ACCENT)
    style.configure("Horizontal.TProgressbar", troughcolor=FIELD, background=ACCENT)
    style.configure("Treeview", background=FIELD, foreground=FG, fieldbackground=FIELD, rowheight=26)
    style.configure("Treeview.Heading", background=PANEL, foreground=FG)
    root.option_add("*Font", ("Malgun Gothic", 10))
