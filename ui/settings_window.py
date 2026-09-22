import customtkinter as ctk

import timer as tmr
from config import FONT, THEMES, shade


# ── helper internal ────────────────────────────────────────────────────────────

def _get_app():
    """Lazy import untuk menghindari circular dependency saat load modul."""
    import ui.app_window as aw
    return aw


# ── show_error ─────────────────────────────────────────────────────────────────

def show_error(message: str) -> None:
    aw = _get_app()

    window = ctk.CTkToplevel(aw.app)
    window.title("Error")
    window.geometry("300x190")
    window.resizable(False, False)
    window.configure(fg_color=aw.T["bg"])
    window.transient(aw.app)
    window.after(100, window.grab_set)

    ctk.CTkLabel(
        window,
        text="oops 🙈",
        font=(FONT, 20, "bold"),
        text_color=aw.T["text"],
    ).pack(pady=(24, 8))

    ctk.CTkLabel(
        window,
        text=message,
        font=(FONT, 13),
        text_color=aw.T["muted"],
        wraplength=250,
    ).pack(pady=5)

    ctk.CTkButton(
        window,
        text="OK",
        width=120,
        height=38,
        corner_radius=19,
        fg_color=aw.T["focus"],
        hover_color=shade(aw.T["focus"], 0.92),
        text_color=aw.T["on_accent"],
        command=window.destroy,
    ).pack(pady=16)


# ── _save_settings (internal) ──────────────────────────────────────────────────

def _save_settings(
    focus_entry,
    break_entry,
    long_break_entry,
    auto_break_checkbox,
    auto_focus_checkbox,
    window,
) -> None:
    aw = _get_app()

    try:
        focus_minutes      = int(focus_entry.get())
        break_minutes      = int(break_entry.get())
        long_break_minutes = int(long_break_entry.get())

        if focus_minutes <= 0 or break_minutes <= 0 or long_break_minutes <= 0:
            raise ValueError

    except ValueError:
        show_error(
            "Masukkan angka yang valid.\n"
            "Semua durasi harus lebih dari 0."
        )
        return

    tmr.pause_timer()

    tmr.FOCUS_TIME      = focus_minutes      * 60
    tmr.BREAK_TIME      = break_minutes      * 60
    tmr.LONG_BREAK_TIME = long_break_minutes * 60

    tmr.auto_start_break = auto_break_checkbox.get() == 1
    tmr.auto_start_focus = auto_focus_checkbox.get() == 1

    tmr.save_current_settings()

    tmr.remaining_time = tmr.mode_duration(tmr.current_mode)

    aw.update_display()

    window.destroy()


# ── open_settings ──────────────────────────────────────────────────────────────

def open_settings() -> None:
    aw = _get_app()

    window = ctk.CTkToplevel(aw.app)
    window.title("Settings")
    window.geometry("340x430")
    window.resizable(False, False)
    window.configure(fg_color=aw.T["bg"])
    window.transient(aw.app)
    window.after(100, window.grab_set)

    ctk.CTkLabel(
        window,
        text="settings ✿",
        font=(FONT, 24, "bold"),
        text_color=aw.T["text"],
    ).pack(pady=(24, 14))

    box = ctk.CTkFrame(window, corner_radius=24, fg_color=aw.T["card"])
    box.pack(fill="x", padx=20)

    entries = []

    fields = (
        ("Focus (min)",      tmr.FOCUS_TIME      // 60),
        ("Break (min)",      tmr.BREAK_TIME      // 60),
        ("Long break (min)", tmr.LONG_BREAK_TIME // 60),
    )

    for label_text, value in fields:
        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(16, 0))

        ctk.CTkLabel(
            row,
            text=label_text,
            font=(FONT, 14),
            text_color=aw.T["text"],
        ).pack(side="left")

        entry = ctk.CTkEntry(
            row,
            width=80,
            justify="center",
            corner_radius=14,
            fg_color=aw.T["bg"],
            border_color=aw.T["track"],
            text_color=aw.T["text"],
        )
        entry.insert(0, str(value))
        entry.pack(side="right")
        entries.append(entry)

    checkbox_style = dict(
        font=(FONT, 14),
        text_color=aw.T["text"],
        fg_color=aw.T["focus"],
        hover_color=shade(aw.T["focus"], 0.92),
        border_color=aw.T["muted"],
        checkmark_color=aw.T["on_accent"],
    )

    auto_break_checkbox = ctk.CTkCheckBox(
        box, text="Auto start break", **checkbox_style
    )
    if tmr.auto_start_break:
        auto_break_checkbox.select()
    auto_break_checkbox.pack(anchor="w", padx=20, pady=(20, 6))

    auto_focus_checkbox = ctk.CTkCheckBox(
        box, text="Auto start focus", **checkbox_style
    )
    if tmr.auto_start_focus:
        auto_focus_checkbox.select()
    auto_focus_checkbox.pack(anchor="w", padx=20, pady=(6, 20))

    ctk.CTkButton(
        window,
        text="Save",
        width=200,
        height=44,
        corner_radius=22,
        font=(FONT, 15, "bold"),
        fg_color=aw.T["focus"],
        hover_color=shade(aw.T["focus"], 0.92),
        text_color=aw.T["on_accent"],
        command=lambda: _save_settings(
            entries[0],
            entries[1],
            entries[2],
            auto_break_checkbox,
            auto_focus_checkbox,
            window,
        ),
    ).pack(pady=22)
