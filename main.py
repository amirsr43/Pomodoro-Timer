import os
import json
import hashlib
import threading
import urllib.request
import winsound
from datetime import date

import customtkinter as ctk
from PIL import Image, ImageOps, ImageSequence
from plyer import notification


# PATHS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Data aplikasi disimpan di AppData
APP_DATA_DIR = os.path.join(
    os.getenv("APPDATA"),
    "pomo"
)

os.makedirs(APP_DATA_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(
    APP_DATA_DIR,
    "settings.json"
)

STATS_FILE = os.path.join(
    APP_DATA_DIR,
    "stats.json"
)

# Cache GIF tetap di folder AppData
CACHE_DIR = os.path.join(
    APP_DATA_DIR,
    "cache"
)

os.makedirs(CACHE_DIR, exist_ok=True)

# Isi dengan LINK langsung ke file .gif (https://...) atau nama file di folder assets/
GIF_SOURCES = {
    "idle": "",        # sebelum start / lagi pause
    "focus": "",      # lagi fokus
    "break": "",      # short break
    "long_break": ""   # long break
}

# Kalau GIF-nya belum ada / gagal didownload, tampil emoji ini
GIF_FALLBACK = {
    "idle": "😴",
    "focus": "🔥",
    "break": "☕",
    "long_break": "🎉"
}

GIF_SIZE = (150, 150)


# SOUND
# Nama file .wav di folder assets/ atau path lengkap, misal r"C:\Music\alarm.wav"
# Kalau file-nya tidak ada, dipakai beep bawaan.
ALARM_SOUND_FILE = "alarm.wav"


# STYLE

FONT = "Segoe UI"

MODES = ["Focus", "Break", "Long Break"]

MODE_KEYS = {
    "Focus": "focus",
    "Break": "break",
    "Long Break": "long_break"
}

IDLE_MESSAGE = {
    "Focus": "ready when you are ✨",
    "Break": "time to recharge ☕",
    "Long Break": "long rest, you earned it 🌸"
}

RUN_MESSAGE = {
    "Focus": "locked in, you got this 🔥",
    "Break": "sip, stretch, breathe ☕",
    "Long Break": "full recharge mode 🌸"
}

# focus / break / long_break = warna aksen tiap mode
THEMES = {
    "Sakura": {
        "mode": "light",
        "bg": "#FFF1F5", "card": "#FFFFFF", "track": "#FBDCE7",
        "text": "#5A3B4B", "muted": "#B98BA0", "on_accent": "#FFFFFF",
        "focus": "#FF7BA9", "break": "#FFAE85", "long_break": "#B79BFF"
    },
    "Matcha": {
        "mode": "light",
        "bg": "#F0F7EA", "card": "#FFFFFF", "track": "#DDEBD0",
        "text": "#3E5A3B", "muted": "#8CA688", "on_accent": "#FFFFFF",
        "focus": "#79B76A", "break": "#F1C063", "long_break": "#66B5C8"
    },
    "Lavender": {
        "mode": "light",
        "bg": "#F3EFFF", "card": "#FFFFFF", "track": "#E4DCFB",
        "text": "#463C70", "muted": "#9E92CB", "on_accent": "#FFFFFF",
        "focus": "#9A7CFF", "break": "#FF9DC4", "long_break": "#63C5E6"
    },
    "Peach": {
        "mode": "light",
        "bg": "#FFF3E8", "card": "#FFFFFF", "track": "#FFE1CC",
        "text": "#6B4232", "muted": "#C39A84", "on_accent": "#FFFFFF",
        "focus": "#FF9466", "break": "#6FCBAE", "long_break": "#FFC45C"
    },
    "Midnight": {
        "mode": "dark",
        "bg": "#15172B", "card": "#20234A", "track": "#2F3366",
        "text": "#EEEBFF", "muted": "#8F94D1", "on_accent": "#15172B",
        "focus": "#8B97FF", "break": "#5FE3C3", "long_break": "#FF92D2"
    }
}


def shade(color, factor):
    color = color.lstrip("#")
    r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))

    return "#%02x%02x%02x" % tuple(
        max(0, min(255, int(c * factor))) for c in (r, g, b)
    )


# LOAD / SAVE

DEFAULT_SETTINGS = {
    "focus": 25,
    "break": 5,
    "long_break": 15,
    "auto_start_break": True,
    "auto_start_focus": True,
    "theme": "Sakura"
}

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            data = json.load(file)

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
    today = str(date.today())

    try:
        with open(STATS_FILE, "r") as file:
            stats = json.load(file)

        if stats["date"] == today:
            return stats["completed"], stats["focus_time"]

    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        pass

    return 0, 0


# CONFIGURATION

_settings = load_settings()

FOCUS_TIME = _settings["focus"] * 60
BREAK_TIME = _settings["break"] * 60
LONG_BREAK_TIME = _settings["long_break"] * 60
auto_start_break = _settings["auto_start_break"]
auto_start_focus = _settings["auto_start_focus"]

theme_name = _settings["theme"]
T = THEMES[theme_name]


# TIMER STATE

remaining_time = FOCUS_TIME
timer_running = False
current_mode = "Focus"
pomodoro_count = 0
timer_id = None
completed_pomodoros, total_focus_time = load_stats()
last_style = None


# GIF PLAYER

class GifPlayer:
    def __init__(self, parent, size):
        self.size = size
        self.cache = {}
        self.frames = []
        self.delays = []
        self.index = 0
        self.job = None
        self.current = None
        self.downloading = set()
        self.failed = set()

        # gambar transparan buat placeholder kalau GIF tidak ada
        blank = Image.new("RGBA", size, (0, 0, 0, 0))
        self.blank = ctk.CTkImage(blank, size=size)

        self.label = ctk.CTkLabel(
            parent,
            text="",
            image=self.blank,
            width=size[0],
            height=size[1],
            font=(FONT, 64)
        )

    def _download(self, url, path):
        # jalan di thread terpisah supaya UI tidak nge-freeze
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)

            request = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(request, timeout=15) as response:
                data = response.read()

            temp_path = path + ".part"

            with open(temp_path, "wb") as file:
                file.write(data)

            os.replace(temp_path, path)

        except Exception:
            self.failed.add(url)

        finally:
            self.downloading.discard(url)

    def _resolve(self, key):
        # return (path, url). url = None kalau file lokal
        source = GIF_SOURCES[key]

        if source.startswith(("http://", "https://")):
            name = hashlib.md5(source.encode()).hexdigest() + ".gif"
            return os.path.join(CACHE_DIR, name), source

        return os.path.join(ASSETS_DIR, source), None

    def load(self, key):
        # return None kalau GIF masih didownload
        if key in self.cache:
            return self.cache[key]

        path, url = self._resolve(key)

        if url is not None and not os.path.exists(path):
            if url in self.failed:
                self.cache[key] = ([], [])
                return self.cache[key]

            if url not in self.downloading:
                self.downloading.add(url)
                threading.Thread(
                    target=self._download,
                    args=(url, path),
                    daemon=True
                ).start()

            return None

        frames, delays = [], []

        try:
            with Image.open(path) as gif:
                for frame in ImageSequence.Iterator(gif):
                    delay = frame.info.get("duration", 100)
                    img = ImageOps.contain(frame.convert("RGBA"), self.size)

                    frames.append(
                        ctk.CTkImage(img, size=img.size)
                    )
                    delays.append(max(20, delay))

        except (FileNotFoundError, OSError):
            frames, delays = [], []

            # link-nya bukan file gambar (misal halaman web) -> buang cache-nya
            if url is not None and os.path.exists(path):
                os.remove(path)

        self.cache[key] = (frames, delays)
        return self.cache[key]

    def play(self, key):
        if key == self.current:
            return

        self.current = key

        if self.job is not None:
            self.label.after_cancel(self.job)
            self.job = None

        result = self.load(key)

        if result is None:
            # masih didownload: tampil emoji dulu, cek lagi sebentar lagi
            self.frames, self.delays = [], []
            self.label.configure(
                image=self.blank,
                text=GIF_FALLBACK[key]
            )
            self.job = self.label.after(
                300,
                lambda: self._retry(key)
            )
            return

        self.frames, self.delays = result
        self.index = 0

        if not self.frames:
            self.label.configure(
                image=self.blank,
                text=GIF_FALLBACK[key]
            )
            return

        self.label.configure(text="")
        self._animate()

    def _retry(self, key):
        self.job = None
        self.current = None
        self.play(key)

    def _animate(self):
        self.label.configure(image=self.frames[self.index])

        if len(self.frames) == 1:
            self.job = None
            return

        delay = self.delays[self.index]
        self.index = (self.index + 1) % len(self.frames)
        self.job = self.label.after(delay, self._animate)


# HELPERS

def mode_duration(mode):
    if mode == "Focus":
        return FOCUS_TIME

    if mode == "Break":
        return BREAK_TIME

    return LONG_BREAK_TIME

def show_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=5
        )
    except Exception:
        pass

def resolve_sound(name):
    if os.path.isabs(name):
        return name

    return os.path.join(ASSETS_DIR, name)

def play_sound():
    # alarm custom (.wav) kalau ada
    path = resolve_sound(ALARM_SOUND_FILE)

    if os.path.exists(path):
        try:
            winsound.PlaySound(
                path,
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
            return
        except Exception:
            pass

    # fallback: beep bawaan, di thread supaya animasi GIF tidak berhenti
    def beep():
        try:
            winsound.Beep(1000, 500)
            winsound.Beep(1200, 500)
        except RuntimeError:
            pass

    threading.Thread(target=beep, daemon=True).start()


# STYLE / THEME

def refresh_style():
    accent = T[MODE_KEYS[current_mode]]

    progress_bar.configure(
        fg_color=T["track"],
        progress_color=accent
    )

    start_pause_button.configure(
        text="⏸  Pause" if timer_running else "▶  Start",
        fg_color=accent,
        hover_color=shade(accent, 0.92),
        text_color=T["on_accent"]
    )

    messages = RUN_MESSAGE if timer_running else IDLE_MESSAGE
    message_label.configure(text=messages[current_mode])

    for mode, button in tab_buttons.items():
        if mode == current_mode:
            color = T[MODE_KEYS[mode]]

            button.configure(
                fg_color=color,
                hover_color=color,
                text_color=T["on_accent"]
            )
        else:
            button.configure(
                fg_color="transparent",
                hover_color=T["track"],
                text_color=T["muted"]
            )

    filled = 4 if current_mode == "Long Break" else pomodoro_count % 4

    for i, dot in enumerate(dots):
        dot.configure(
            fg_color=accent if i < filled else T["track"]
        )

    for name, swatch in swatch_buttons.items():
        swatch.configure(
            border_color=T["text"] if name == theme_name else T["bg"]
        )

def apply_theme(name):
    global theme_name, T, last_style

    theme_name = name
    T = THEMES[name]

    ctk.set_appearance_mode(T["mode"])

    app.configure(fg_color=T["bg"])

    title_label.configure(text_color=T["text"])

    settings_button.configure(
        fg_color=T["card"],
        hover_color=T["track"],
        text_color=T["text"]
    )

    tabs_frame.configure(fg_color=T["card"])

    card.configure(
        fg_color=T["card"],
        border_color=T["track"]
    )

    gif_player.label.configure(text_color=T["text"])
    timer_label.configure(text_color=T["text"])
    message_label.configure(text_color=T["muted"])

    reset_button.configure(
        fg_color=T["card"],
        hover_color=T["track"],
        text_color=T["text"]
    )

    for chip in stat_chips:
        chip.configure(fg_color=T["card"])

    for label in stat_values:
        label.configure(text_color=T["text"])

    for label in stat_titles:
        label.configure(text_color=T["muted"])

    last_style = None
    update_display()

def choose_theme(name):
    apply_theme(name)
    save_settings_file()


# DISPLAY

def update_gif():
    if not timer_running:
        gif_player.play("idle")
    else:
        gif_player.play(MODE_KEYS[current_mode])

def update_progress():
    progress = remaining_time / mode_duration(current_mode)

    progress_bar.set(progress)

def update_display():
    global last_style

    minutes = remaining_time // 60
    seconds = remaining_time % 60

    timer_label.configure(
        text=f"{minutes:02d}:{seconds:02d}"
    )

    completed_value.configure(
        text=str(completed_pomodoros)
    )

    focus_value.configure(
        text=f"{total_focus_time} min"
    )

    style_key = (
        theme_name,
        current_mode,
        timer_running,
        pomodoro_count
    )

    if style_key != last_style:
        last_style = style_key
        refresh_style()

    update_progress()
    update_gif()


# TIMER

def update_timer():
    global remaining_time, timer_id

    update_display()

    if not timer_running:
        timer_id = None
        return

    if remaining_time > 0:
        remaining_time -= 1

        timer_id = app.after(
            1000,
            update_timer
        )

    else:
        switch_mode()


def start_timer():
    global timer_running

    if timer_running:
        return

    timer_running = True
    update_timer()


def pause_timer():
    global timer_running, timer_id

    timer_running = False

    if timer_id is not None:
        app.after_cancel(timer_id)
        timer_id = None

    update_display()


def reset_timer():
    global remaining_time

    pause_timer()

    remaining_time = mode_duration(current_mode)

    update_display()

def toggle_timer():
    if timer_running:
        pause_timer()
    else:
        start_timer()

def select_mode(mode):
    global current_mode, remaining_time

    pause_timer()

    current_mode = mode
    remaining_time = mode_duration(mode)

    update_display()


def switch_mode():
    global remaining_time
    global current_mode
    global pomodoro_count
    global timer_id
    global timer_running
    global completed_pomodoros
    global total_focus_time

    timer_id = None

    if current_mode == "Focus":
        pomodoro_count += 1

        completed_pomodoros += 1
        total_focus_time += FOCUS_TIME // 60

        save_stats()
        play_sound()

        if pomodoro_count % 4 == 0:
            current_mode = "Long Break"
            remaining_time = LONG_BREAK_TIME

            show_notification(
                "Pomodoro",
                "4 Pomodoro selesai! Saatnya long break 🎉"
            )

        else:
            current_mode = "Break"
            remaining_time = BREAK_TIME

            show_notification(
                "Pomodoro",
                "Focus selesai! Saatnya istirahat ☕"
            )

        auto_start = auto_start_break

    else:
        current_mode = "Focus"
        remaining_time = FOCUS_TIME

        play_sound()

        show_notification(
            "Pomodoro",
            "Break selesai! Saatnya kembali fokus 💻"
        )

        auto_start = auto_start_focus

    if auto_start:
        timer_id = app.after(1000, update_timer)
    else:
        timer_running = False

    update_display()


# SETTINGS WINDOW

def open_settings():
    window = ctk.CTkToplevel(app)

    window.title("Settings")
    window.geometry("340x430")
    window.resizable(False, False)
    window.configure(fg_color=T["bg"])

    window.transient(app)
    window.after(100, window.grab_set)

    ctk.CTkLabel(
        window,
        text="settings ✿",
        font=(FONT, 24, "bold"),
        text_color=T["text"]
    ).pack(pady=(24, 14))

    box = ctk.CTkFrame(
        window,
        corner_radius=24,
        fg_color=T["card"]
    )
    box.pack(fill="x", padx=20)

    entries = []

    fields = (
        ("Focus (min)", FOCUS_TIME // 60),
        ("Break (min)", BREAK_TIME // 60),
        ("Long break (min)", LONG_BREAK_TIME // 60)
    )

    for label_text, value in fields:
        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(16, 0))

        ctk.CTkLabel(
            row,
            text=label_text,
            font=(FONT, 14),
            text_color=T["text"]
        ).pack(side="left")

        entry = ctk.CTkEntry(
            row,
            width=80,
            justify="center",
            corner_radius=14,
            fg_color=T["bg"],
            border_color=T["track"],
            text_color=T["text"]
        )
        entry.insert(0, str(value))
        entry.pack(side="right")

        entries.append(entry)

    checkbox_style = dict(
        font=(FONT, 14),
        text_color=T["text"],
        fg_color=T["focus"],
        hover_color=shade(T["focus"], 0.92),
        border_color=T["muted"],
        checkmark_color=T["on_accent"]
    )

    auto_break_checkbox = ctk.CTkCheckBox(
        box,
        text="Auto start break",
        **checkbox_style
    )

    if auto_start_break:
        auto_break_checkbox.select()

    auto_break_checkbox.pack(anchor="w", padx=20, pady=(20, 6))

    auto_focus_checkbox = ctk.CTkCheckBox(
        box,
        text="Auto start focus",
        **checkbox_style
    )

    if auto_start_focus:
        auto_focus_checkbox.select()

    auto_focus_checkbox.pack(anchor="w", padx=20, pady=(6, 20))

    ctk.CTkButton(
        window,
        text="Save",
        width=200,
        height=44,
        corner_radius=22,
        font=(FONT, 15, "bold"),
        fg_color=T["focus"],
        hover_color=shade(T["focus"], 0.92),
        text_color=T["on_accent"],
        command=lambda: save_settings(
            entries[0],
            entries[1],
            entries[2],
            auto_break_checkbox,
            auto_focus_checkbox,
            window
        )
    ).pack(pady=22)

def show_error(message):
    window = ctk.CTkToplevel(app)

    window.title("Error")
    window.geometry("300x190")
    window.resizable(False, False)
    window.configure(fg_color=T["bg"])

    window.transient(app)
    window.after(100, window.grab_set)

    ctk.CTkLabel(
        window,
        text="oops 🙈",
        font=(FONT, 20, "bold"),
        text_color=T["text"]
    ).pack(pady=(24, 8))

    ctk.CTkLabel(
        window,
        text=message,
        font=(FONT, 13),
        text_color=T["muted"],
        wraplength=250
    ).pack(pady=5)

    ctk.CTkButton(
        window,
        text="OK",
        width=120,
        height=38,
        corner_radius=19,
        fg_color=T["focus"],
        hover_color=shade(T["focus"], 0.92),
        text_color=T["on_accent"],
        command=window.destroy
    ).pack(pady=16)

def save_settings(
    focus_entry,
    break_entry,
    long_break_entry,
    auto_break_checkbox,
    auto_focus_checkbox,
    window
):
    global FOCUS_TIME
    global BREAK_TIME
    global LONG_BREAK_TIME
    global remaining_time
    global auto_start_break
    global auto_start_focus

    try:
        focus_minutes = int(focus_entry.get())
        break_minutes = int(break_entry.get())
        long_break_minutes = int(long_break_entry.get())

        if (
            focus_minutes <= 0
            or break_minutes <= 0
            or long_break_minutes <= 0
        ):
            raise ValueError

    except ValueError:
        show_error(
            "Masukkan angka yang valid.\n"
            "Semua durasi harus lebih dari 0."
        )
        return

    pause_timer()

    FOCUS_TIME = focus_minutes * 60
    BREAK_TIME = break_minutes * 60
    LONG_BREAK_TIME = long_break_minutes * 60

    auto_start_break = auto_break_checkbox.get() == 1
    auto_start_focus = auto_focus_checkbox.get() == 1

    save_settings_file()

    remaining_time = mode_duration(current_mode)

    update_display()

    window.destroy()


def save_settings_file():
    settings = {
        "focus": FOCUS_TIME // 60,
        "break": BREAK_TIME // 60,
        "long_break": LONG_BREAK_TIME // 60,
        "auto_start_break": auto_start_break,
        "auto_start_focus": auto_start_focus,
        "theme": theme_name
    }

    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)
        
def save_stats():
    stats = {
        "date": str(date.today()),
        "completed": completed_pomodoros,
        "focus_time": total_focus_time
    }

    with open(STATS_FILE, "w") as file:
        json.dump(stats, file, indent=4)

# APP

app = ctk.CTk()

app.title("pomo")
app.geometry("440x720")
app.resizable(False, False)


# HEADER

header = ctk.CTkFrame(app, fg_color="transparent")
header.pack(fill="x", padx=24, pady=(22, 14))

title_label = ctk.CTkLabel(
    header,
    text="🍅 pomo",
    font=(FONT, 26, "bold")
)
title_label.pack(side="left")

settings_button = ctk.CTkButton(
    header,
    text="⚙",
    width=38,
    height=38,
    corner_radius=19,
    font=(FONT, 16),
    command=open_settings
)
settings_button.pack(side="right")

swatch_frame = ctk.CTkFrame(header, fg_color="transparent")
swatch_frame.pack(side="right", padx=(0, 10))

swatch_buttons = {}

for _name, _theme in THEMES.items():
    swatch = ctk.CTkButton(
        swatch_frame,
        text="",
        width=24,
        height=24,
        corner_radius=12,
        border_width=3,
        fg_color=_theme["focus"],
        hover_color=shade(_theme["focus"], 0.9),
        command=lambda n=_name: choose_theme(n)
    )
    swatch.pack(side="left", padx=2)

    swatch_buttons[_name] = swatch


# MODE TABS

tabs_frame = ctk.CTkFrame(
    app,
    corner_radius=26,
    height=52
)
tabs_frame.pack(fill="x", padx=24, pady=(0, 16))

tabs_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="tab")

tab_buttons = {}

for _i, _mode in enumerate(MODES):
    tab = ctk.CTkButton(
        tabs_frame,
        text=_mode,
        width=110,
        height=40,
        corner_radius=20,
        border_width=0,
        font=(FONT, 13, "bold"),
        command=lambda m=_mode: select_mode(m)
    )
    tab.grid(row=0, column=_i, padx=6, pady=6, sticky="ew")

    tab_buttons[_mode] = tab


# MAIN CARD

card = ctk.CTkFrame(
    app,
    corner_radius=36,
    border_width=2
)
card.pack(fill="x", padx=24)

gif_player = GifPlayer(card, GIF_SIZE)
gif_player.label.pack(pady=(24, 0))

timer_label = ctk.CTkLabel(
    card,
    text=f"{FOCUS_TIME // 60:02d}:00",
    font=(FONT, 72, "bold")
)
timer_label.pack(pady=(0, 0))

message_label = ctk.CTkLabel(
    card,
    text="",
    font=(FONT, 14)
)
message_label.pack(pady=(0, 14))

dots_frame = ctk.CTkFrame(card, fg_color="transparent")
dots_frame.pack(pady=(0, 16))

dots = []

for _i in range(4):
    dot = ctk.CTkFrame(
        dots_frame,
        width=12,
        height=12,
        corner_radius=6
    )
    dot.grid(row=0, column=_i, padx=5)

    dots.append(dot)

progress_bar = ctk.CTkProgressBar(
    card,
    width=300,
    height=10,
    corner_radius=5
)
progress_bar.pack(pady=(0, 28))

progress_bar.set(1)


# CONTROLS

controls = ctk.CTkFrame(app, fg_color="transparent")
controls.pack(pady=18)

reset_button = ctk.CTkButton(
    controls,
    text="↻",
    width=56,
    height=56,
    corner_radius=28,
    font=(FONT, 20),
    command=reset_timer
)
reset_button.pack(side="left", padx=(0, 12))

start_pause_button = ctk.CTkButton(
    controls,
    text="▶  Start",
    width=220,
    height=56,
    corner_radius=28,
    font=(FONT, 18, "bold"),
    command=toggle_timer
)
start_pause_button.pack(side="left")


# STATS

stats_frame = ctk.CTkFrame(app, fg_color="transparent")
stats_frame.pack(fill="x", padx=24)

stats_frame.grid_columnconfigure((0, 1), weight=1, uniform="stat")

stat_chips = []
stat_values = []
stat_titles = []

_stat_defs = (("Completed today", "0"), ("Focus time", "0 min"))

for _i, (_title, _value) in enumerate(_stat_defs):
    chip = ctk.CTkFrame(
        stats_frame,
        corner_radius=24,
        height=76
    )
    chip.grid(row=0, column=_i, padx=6, sticky="ew")
    chip.grid_propagate(False)
    chip.grid_columnconfigure(0, weight=1)
    chip.grid_rowconfigure((0, 1), weight=1)

    value_label = ctk.CTkLabel(
        chip,
        text=_value,
        font=(FONT, 22, "bold")
    )
    value_label.grid(row=0, column=0, sticky="s", pady=(8, 0))

    title_label_ = ctk.CTkLabel(
        chip,
        text=_title,
        font=(FONT, 12)
    )
    title_label_.grid(row=1, column=0, sticky="n", pady=(0, 8))

    stat_chips.append(chip)
    stat_values.append(value_label)
    stat_titles.append(title_label_)

completed_value, focus_value = stat_values


# INITIAL DISPLAY

apply_theme(theme_name)

app.mainloop()