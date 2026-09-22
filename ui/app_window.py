import customtkinter as ctk

import timer as tmr
from config import (
    FONT, MODES, MODE_KEYS, IDLE_MESSAGE, RUN_MESSAGE,
    THEMES, GIF_SIZE, shade,
)
from gif_player import GifPlayer
from ui.settings_window import open_settings

# ── Root window ────────────────────────────────────────────────────────────────

app = ctk.CTk()
app.title("pomo")
app.geometry("440x720")
app.resizable(False, False)

# ── Theme state ────────────────────────────────────────────────────────────────

theme_name = tmr.theme_name
T          = THEMES[theme_name]
last_style = None

# ── HEADER ─────────────────────────────────────────────────────────────────────

header = ctk.CTkFrame(app, fg_color="transparent")
header.pack(fill="x", padx=24, pady=(22, 14))

title_label = ctk.CTkLabel(
    header,
    text="🍅 pomo",
    font=(FONT, 26, "bold"),
)
title_label.pack(side="left")

settings_button = ctk.CTkButton(
    header,
    text="⚙",
    width=38,
    height=38,
    corner_radius=19,
    font=(FONT, 16),
    command=open_settings,
)
settings_button.pack(side="right")

swatch_frame = ctk.CTkFrame(header, fg_color="transparent")
swatch_frame.pack(side="right", padx=(0, 10))

swatch_buttons = {}

for _name, _theme in THEMES.items():
    _swatch = ctk.CTkButton(
        swatch_frame,
        text="",
        width=24,
        height=24,
        corner_radius=12,
        border_width=3,
        fg_color=_theme["focus"],
        hover_color=shade(_theme["focus"], 0.9),
        command=lambda n=_name: choose_theme(n),
    )
    _swatch.pack(side="left", padx=2)
    swatch_buttons[_name] = _swatch

# ── MODE TABS ──────────────────────────────────────────────────────────────────

tabs_frame = ctk.CTkFrame(app, corner_radius=26, height=52)
tabs_frame.pack(fill="x", padx=24, pady=(0, 16))
tabs_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="tab")

tab_buttons = {}

for _i, _mode in enumerate(MODES):
    _tab = ctk.CTkButton(
        tabs_frame,
        text=_mode,
        width=110,
        height=40,
        corner_radius=20,
        border_width=0,
        font=(FONT, 13, "bold"),
        command=lambda m=_mode: tmr.select_mode(m),
    )
    _tab.grid(row=0, column=_i, padx=6, pady=6, sticky="ew")
    tab_buttons[_mode] = _tab

# ── MAIN CARD ──────────────────────────────────────────────────────────────────

card = ctk.CTkFrame(app, corner_radius=36, border_width=2)
card.pack(fill="x", padx=24)

gif_player = GifPlayer(card, GIF_SIZE)
gif_player.label.pack(pady=(24, 0))

timer_label = ctk.CTkLabel(
    card,
    text=f"{tmr.FOCUS_TIME // 60:02d}:00",
    font=(FONT, 72, "bold"),
)
timer_label.pack(pady=(0, 0))

message_label = ctk.CTkLabel(card, text="", font=(FONT, 14))
message_label.pack(pady=(0, 14))

dots_frame = ctk.CTkFrame(card, fg_color="transparent")
dots_frame.pack(pady=(0, 16))

dots = []

for _i in range(4):
    _dot = ctk.CTkFrame(dots_frame, width=12, height=12, corner_radius=6)
    _dot.grid(row=0, column=_i, padx=5)
    dots.append(_dot)

progress_bar = ctk.CTkProgressBar(card, width=300, height=10, corner_radius=5)
progress_bar.pack(pady=(0, 28))
progress_bar.set(1)

# ── CONTROLS ───────────────────────────────────────────────────────────────────

controls = ctk.CTkFrame(app, fg_color="transparent")
controls.pack(pady=18)

reset_button = ctk.CTkButton(
    controls,
    text="↻",
    width=56,
    height=56,
    corner_radius=28,
    font=(FONT, 20),
    command=tmr.reset_timer,
)
reset_button.pack(side="left", padx=(0, 12))

start_pause_button = ctk.CTkButton(
    controls,
    text="▶  Start",
    width=220,
    height=56,
    corner_radius=28,
    font=(FONT, 18, "bold"),
    command=tmr.toggle_timer,
)
start_pause_button.pack(side="left")

# ── STATS ──────────────────────────────────────────────────────────────────────

stats_frame = ctk.CTkFrame(app, fg_color="transparent")
stats_frame.pack(fill="x", padx=24)
stats_frame.grid_columnconfigure((0, 1), weight=1, uniform="stat")

stat_chips  = []
stat_values = []
stat_titles = []

_stat_defs = (("Completed today", "0"), ("Focus time", "0 min"))

for _i, (_title, _val) in enumerate(_stat_defs):
    _chip = ctk.CTkFrame(stats_frame, corner_radius=24, height=76)
    _chip.grid(row=0, column=_i, padx=6, sticky="ew")
    _chip.grid_propagate(False)
    _chip.grid_columnconfigure(0, weight=1)
    _chip.grid_rowconfigure((0, 1), weight=1)

    _value_label = ctk.CTkLabel(_chip, text=_val, font=(FONT, 22, "bold"))
    _value_label.grid(row=0, column=0, sticky="s", pady=(8, 0))

    _title_label = ctk.CTkLabel(_chip, text=_title, font=(FONT, 12))
    _title_label.grid(row=1, column=0, sticky="n", pady=(0, 8))

    stat_chips.append(_chip)
    stat_values.append(_value_label)
    stat_titles.append(_title_label)

completed_value, focus_value = stat_values

# ── DISPLAY ────────────────────────────────────────────────────────────────────

def update_gif() -> None:
    if not tmr.timer_running:
        gif_player.play("idle")
    else:
        gif_player.play(MODE_KEYS[tmr.current_mode])


def update_progress() -> None:
    progress = tmr.remaining_time / tmr.mode_duration(tmr.current_mode)
    progress_bar.set(progress)


def refresh_style() -> None:
    accent = T[MODE_KEYS[tmr.current_mode]]

    progress_bar.configure(fg_color=T["track"], progress_color=accent)

    start_pause_button.configure(
        text="⏸  Pause" if tmr.timer_running else "▶  Start",
        fg_color=accent,
        hover_color=shade(accent, 0.92),
        text_color=T["on_accent"],
    )

    messages = RUN_MESSAGE if tmr.timer_running else IDLE_MESSAGE
    message_label.configure(text=messages[tmr.current_mode])

    for mode, button in tab_buttons.items():
        if mode == tmr.current_mode:
            color = T[MODE_KEYS[mode]]
            button.configure(
                fg_color=color,
                hover_color=color,
                text_color=T["on_accent"],
            )
        else:
            button.configure(
                fg_color="transparent",
                hover_color=T["track"],
                text_color=T["muted"],
            )

    filled = 4 if tmr.current_mode == "Long Break" else tmr.pomodoro_count % 4

    for i, dot in enumerate(dots):
        dot.configure(fg_color=accent if i < filled else T["track"])

    for name, swatch in swatch_buttons.items():
        swatch.configure(
            border_color=T["text"] if name == theme_name else T["bg"]
        )


def update_display() -> None:
    global last_style

    minutes = tmr.remaining_time // 60
    seconds = tmr.remaining_time % 60
    timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")

    completed_value.configure(text=str(tmr.completed_pomodoros))
    focus_value.configure(text=f"{tmr.total_focus_time} min")

    style_key = (
        theme_name,
        tmr.current_mode,
        tmr.timer_running,
        tmr.pomodoro_count,
    )

    if style_key != last_style:
        last_style = style_key
        refresh_style()

    update_progress()
    update_gif()

# ── THEME ──────────────────────────────────────────────────────────────────────

def apply_theme(name: str) -> None:
    global theme_name, T, last_style

    theme_name     = name
    T              = THEMES[name]
    tmr.theme_name = name  # sync ke timer (untuk save_current_settings)

    ctk.set_appearance_mode(T["mode"])

    app.configure(fg_color=T["bg"])
    title_label.configure(text_color=T["text"])

    settings_button.configure(
        fg_color=T["card"],
        hover_color=T["track"],
        text_color=T["text"],
    )

    tabs_frame.configure(fg_color=T["card"])

    card.configure(fg_color=T["card"], border_color=T["track"])

    gif_player.label.configure(text_color=T["text"])
    timer_label.configure(text_color=T["text"])
    message_label.configure(text_color=T["muted"])

    reset_button.configure(
        fg_color=T["card"],
        hover_color=T["track"],
        text_color=T["text"],
    )

    for chip in stat_chips:
        chip.configure(fg_color=T["card"])

    for label in stat_values:
        label.configure(text_color=T["text"])

    for label in stat_titles:
        label.configure(text_color=T["muted"])

    last_style = None
    update_display()


def choose_theme(name: str) -> None:
    apply_theme(name)
    tmr.save_current_settings()

# ── INIT ───────────────────────────────────────────────────────────────────────

def build() -> None:
    """Hubungkan timer ke app window, lalu terapkan tema awal."""
    tmr.init(app, update_display)
    apply_theme(theme_name)
