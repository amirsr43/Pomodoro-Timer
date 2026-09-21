# 🍅 Pomodoro-Timer

A cute, aesthetic Pomodoro timer for your desktop, built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). It has animated GIFs, pastel themes, and an alarm sound you can swap for your own.

<!-- Add a screenshot: put it at assets/screenshot.png, then uncomment the line below -->
<!-- <img src="assets/screenshot.png" width="320" alt="Pomodoro Timer screenshot" /> -->

## ✨ Features

- **Three modes**: Focus, Break, and Long Break. Switch between them with one click.
- **Animated GIFs** for each state: idle (before start or while paused), focus, break, and long break. Use a direct link or a local file.
- **5 themes**: 🌸 Sakura, 🍵 Matcha, 💜 Lavender, 🍑 Peach, 🌙 Midnight. Pick one from the colored dots in the header.
- **Auto cycle**: 4 focus sessions, then a long break. Auto start for break and focus can be toggled.
- **Custom alarm**: plays when a session ends, with your own `.wav` if you want.
- **Desktop notifications** when it's time to rest or get back to work.
- **Daily stats**: completed pomodoros and total focus minutes, reset every day.
- **Remembers your settings**: durations, auto start, and theme are saved.

## 📦 Requirements

- Windows (the alarm uses the built-in `winsound` module)
- Python 3.8 or newer
- `customtkinter`, `pillow`, `plyer`

## 🚀 Getting Started

```bash
# 1. clone the repo
git clone https://github.com/amirsr43/Pomodoro-Timer.git
cd Pomodoro-Timer

# 2. install dependencies
pip install customtkinter pillow plyer

# 3. run it
python pomodoro.py
```

## 🎮 How to Use

1. Pick a mode: **Focus**, **Break**, or **Long Break**.
2. Press **Start**. The GIF changes to match the mode and the progress bar shrinks as time runs out.
3. **↻** resets the current timer. **⚙** opens settings.
4. When a session ends, you get an alarm and a notification, and the next mode begins (if auto start is on).

The four dots under the timer show your progress toward the next long break.

## 🎨 Customization

### Durations and auto start

Open **⚙ Settings** to change focus, break, and long break minutes, and to toggle auto start. Defaults are 25 / 5 / 15.

### GIFs

At the top of `pomodoro.py`, edit `GIF_SOURCES`. Each entry can be a **direct link** to a `.gif` or a **file name** inside `assets/`:

```python
GIF_SOURCES = {
    "idle": "https://example.com/idle.gif",
    "focus": "focus.gif",              # assets/focus.gif
    "break": "https://example.com/break.gif",
    "long_break": "long_break.gif"
}
```

- Links must point straight to the image file (ending in `.gif`), not a web page. On Giphy or Tenor, right-click the GIF and choose "Copy image address".
- Downloaded GIFs are cached in `assets/cache/`, so they only download once.
- If a GIF is missing or fails to load, an emoji is shown instead.
- Keep GIFs small (under about 100 frames) so they load quickly.

### Alarm sound

Put a file named `alarm.wav` in `assets/`, or change `ALARM_SOUND_FILE` in `pomodoro.py`. It can be a file name or a full path:

```python
ALARM_SOUND_FILE = r"C:\Music\ding.wav"
```

If no file is found, a default beep is used. Only `.wav` files are supported. Convert mp3 files first.

### Themes

Add a new entry to the `THEMES` dictionary in `pomodoro.py` and its color dot appears in the header automatically:

```python
"Ocean": {
    "mode": "light",
    "bg": "#EEF7FB", "card": "#FFFFFF", "track": "#D6EAF3",
    "text": "#2F4A5A", "muted": "#7FA3B5", "on_accent": "#FFFFFF",
    "focus": "#4FA8D8", "break": "#7FD1B9", "long_break": "#A78BFA"
}
```

## 🗂️ Project Structure

```
Pomodoro-Timer/
├── main.py
├── assets/          # optional local assets
├── .gitignore
└── README.md
```

## 📝 Notes

- The app is Windows-only because of `winsound`. On macOS or Linux, replace the `play_sound` function with another audio library.
- `settings.json`, `stats.json`, and `assets/cache/` are generated at runtime. You may want to add them to `.gitignore`.
- Run the app from its own folder so it finds `settings.json` and `stats.json`.

## 📄 License

Free to use and modify. Add a license file if you plan to share it publicly.

---

<div align="center">
  made with 🍅 and too many hover animations
</div>
