import json
from datetime import date

from config import SETTINGS_FILE, STATS_FILE, THEMES

DEFAULT_SETTINGS = {
    "focus":            25,
    "break":            5,
    "long_break":       15,
    "auto_start_break": True,
    "auto_start_focus": True,
    "theme":            "Sakura",
}


def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    settings = {**DEFAULT_SETTINGS, **data}

    for key in ("focus", "break", "long_break"):
        if not isinstance(settings[key], int) or settings[key] <= 0:
            settings[key] = DEFAULT_SETTINGS[key]

    if settings["theme"] not in THEMES:
        settings["theme"] = DEFAULT_SETTINGS["theme"]

    return settings


def load_stats():
    """Return (completed_pomodoros, total_focus_time_minutes) untuk hari ini."""
    today = str(date.today())

    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)

        if stats["date"] == today:
            return stats["completed"], stats["focus_time"]

    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        pass

    return 0, 0


def save_settings_file(
    focus_min: int,
    break_min: int,
    long_break_min: int,
    auto_start_break: bool,
    auto_start_focus: bool,
    theme_name: str,
) -> None:
    settings = {
        "focus":            focus_min,
        "break":            break_min,
        "long_break":       long_break_min,
        "auto_start_break": auto_start_break,
        "auto_start_focus": auto_start_focus,
        "theme":            theme_name,
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)


def save_stats(completed_pomodoros: int, total_focus_time: int) -> None:
    stats = {
        "date":       str(date.today()),
        "completed":  completed_pomodoros,
        "focus_time": total_focus_time,
    }
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)
