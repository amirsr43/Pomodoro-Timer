from data import load_settings, load_stats, save_settings_file, save_stats
from sound import play_sound, show_notification

# ── load settings ──────────────────────────────────────────────────────────────

_settings = load_settings()

FOCUS_TIME       = _settings["focus"]      * 60
BREAK_TIME       = _settings["break"]      * 60
LONG_BREAK_TIME  = _settings["long_break"] * 60
auto_start_break = _settings["auto_start_break"]
auto_start_focus = _settings["auto_start_focus"]
theme_name       = _settings["theme"]

# ── timer state ────────────────────────────────────────────────────────────────

remaining_time     = FOCUS_TIME
timer_running      = False
current_mode       = "Focus"
pomodoro_count     = 0
timer_id           = None

completed_pomodoros, total_focus_time = load_stats()

# ── UI callbacks (diisi oleh ui/app_window.py setelah widget dibuat) ───────────
# Pola ini menghindari circular import: timer tidak pernah mengimport dari ui.

_app        = None   # CTk root window
_display_cb = None   # fungsi update_display()


def init(app_instance, display_callback) -> None:
    """Hubungkan timer ke app window dan callback display."""
    global _app, _display_cb
    _app        = app_instance
    _display_cb = display_callback


def _call_display() -> None:
    if _display_cb is not None:
        _display_cb()


# ── helpers ────────────────────────────────────────────────────────────────────

def mode_duration(mode: str) -> int:
    if mode == "Focus":
        return FOCUS_TIME
    if mode == "Break":
        return BREAK_TIME
    return LONG_BREAK_TIME


# ── save helpers ───────────────────────────────────────────────────────────────

def save_current_settings() -> None:
    """Simpan state settings aktif ke file."""
    save_settings_file(
        FOCUS_TIME      // 60,
        BREAK_TIME      // 60,
        LONG_BREAK_TIME // 60,
        auto_start_break,
        auto_start_focus,
        theme_name,
    )


def save_current_stats() -> None:
    save_stats(completed_pomodoros, total_focus_time)


# ── timer logic ────────────────────────────────────────────────────────────────

def update_timer() -> None:
    global remaining_time, timer_id

    _call_display()

    if not timer_running:
        timer_id = None
        return

    if remaining_time > 0:
        remaining_time -= 1
        timer_id = _app.after(1000, update_timer)
    else:
        switch_mode()


def start_timer() -> None:
    global timer_running

    if timer_running:
        return

    timer_running = True
    update_timer()


def pause_timer() -> None:
    global timer_running, timer_id

    timer_running = False

    if timer_id is not None:
        _app.after_cancel(timer_id)
        timer_id = None

    _call_display()


def reset_timer() -> None:
    global remaining_time

    pause_timer()
    remaining_time = mode_duration(current_mode)
    _call_display()


def toggle_timer() -> None:
    if timer_running:
        pause_timer()
    else:
        start_timer()


def select_mode(mode: str) -> None:
    global current_mode, remaining_time

    pause_timer()
    current_mode   = mode
    remaining_time = mode_duration(mode)
    _call_display()


def switch_mode() -> None:
    global remaining_time, current_mode, pomodoro_count
    global timer_id, timer_running
    global completed_pomodoros, total_focus_time

    timer_id = None

    if current_mode == "Focus":
        pomodoro_count      += 1
        completed_pomodoros += 1
        total_focus_time    += FOCUS_TIME // 60

        save_current_stats()
        play_sound()

        if pomodoro_count % 4 == 0:
            current_mode   = "Long Break"
            remaining_time = LONG_BREAK_TIME
            show_notification("Pomodoro", "4 Pomodoro selesai! Saatnya long break 🎉")
        else:
            current_mode   = "Break"
            remaining_time = BREAK_TIME
            show_notification("Pomodoro", "Focus selesai! Saatnya istirahat ☕")

        auto_start = auto_start_break

    else:
        current_mode   = "Focus"
        remaining_time = FOCUS_TIME

        play_sound()
        show_notification("Pomodoro", "Break selesai! Saatnya kembali fokus 💻")

        auto_start = auto_start_focus

    if auto_start:
        timer_id = _app.after(1000, update_timer)
    else:
        timer_running = False

    _call_display()
