import os

# ── PATHS ──────────────────────────────────────────────────────────────────────

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

APP_DATA_DIR = os.path.join(os.getenv("APPDATA"), "pomo")
os.makedirs(APP_DATA_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(APP_DATA_DIR, "settings.json")
STATS_FILE    = os.path.join(APP_DATA_DIR, "stats.json")
CACHE_DIR     = os.path.join(APP_DATA_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# ── GIF ────────────────────────────────────────────────────────────────────────
# Isi dengan link langsung ke file .gif (https://...) atau nama file di folder assets/

GIF_SOURCES = {
    "idle":       "",   # sebelum start / lagi pause
    "focus":      "",   # lagi fokus
    "break":      "",   # short break
    "long_break": "",   # long break
}

# Kalau GIF-nya belum ada / gagal didownload, tampil emoji ini
GIF_FALLBACK = {
    "idle":       "😴",
    "focus":      "🔥",
    "break":      "☕",
    "long_break": "🎉",
}

GIF_SIZE = (150, 150)

# ── SOUND ──────────────────────────────────────────────────────────────────────
# Nama file .wav di folder assets/ atau path lengkap, misal r"C:\Music\alarm.wav"
# Kalau file-nya tidak ada, dipakai beep bawaan.
ALARM_SOUND_FILE = "alarm.wav"

# ── STYLE ──────────────────────────────────────────────────────────────────────

FONT = "Segoe UI"

MODES     = ["Focus", "Break", "Long Break"]
MODE_KEYS = {
    "Focus":      "focus",
    "Break":      "break",
    "Long Break": "long_break",
}

IDLE_MESSAGE = {
    "Focus":      "ready when you are ✨",
    "Break":      "time to recharge ☕",
    "Long Break": "long rest, you earned it 🌸",
}

RUN_MESSAGE = {
    "Focus":      "locked in, you got this 🔥",
    "Break":      "sip, stretch, breathe ☕",
    "Long Break": "full recharge mode 🌸",
}

# Tiap tema punya kunci: mode, bg, card, track, text, muted, on_accent,
# dan warna aksen per mode: focus / break / long_break
THEMES = {
    "Sakura": {
        "mode": "light",
        "bg": "#FFF1F5", "card": "#FFFFFF", "track": "#FBDCE7",
        "text": "#5A3B4B", "muted": "#B98BA0", "on_accent": "#FFFFFF",
        "focus": "#FF7BA9", "break": "#FFAE85", "long_break": "#B79BFF",
    },
    "Matcha": {
        "mode": "light",
        "bg": "#F0F7EA", "card": "#FFFFFF", "track": "#DDEBD0",
        "text": "#3E5A3B", "muted": "#8CA688", "on_accent": "#FFFFFF",
        "focus": "#79B76A", "break": "#F1C063", "long_break": "#66B5C8",
    },
    "Lavender": {
        "mode": "light",
        "bg": "#F3EFFF", "card": "#FFFFFF", "track": "#E4DCFB",
        "text": "#463C70", "muted": "#9E92CB", "on_accent": "#FFFFFF",
        "focus": "#9A7CFF", "break": "#FF9DC4", "long_break": "#63C5E6",
    },
    "Peach": {
        "mode": "light",
        "bg": "#FFF3E8", "card": "#FFFFFF", "track": "#FFE1CC",
        "text": "#6B4232", "muted": "#C39A84", "on_accent": "#FFFFFF",
        "focus": "#FF9466", "break": "#6FCBAE", "long_break": "#FFC45C",
    },
    "Midnight": {
        "mode": "dark",
        "bg": "#15172B", "card": "#20234A", "track": "#2F3366",
        "text": "#EEEBFF", "muted": "#8F94D1", "on_accent": "#15172B",
        "focus": "#8B97FF", "break": "#5FE3C3", "long_break": "#FF92D2",
    },
}


def shade(color: str, factor: float) -> str:
    """Gelap/terangin warna hex dengan mengalikan nilai RGB-nya dengan factor."""
    color  = color.lstrip("#")
    r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(
        max(0, min(255, int(c * factor))) for c in (r, g, b)
    )
