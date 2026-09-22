# 🍅 Pomodoro-Timer

<<<<<<< HEAD
A cute, aesthetic Pomodoro timer for your desktop, built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). It has animated GIFs, pastel themes, and an alarm sound you can swap for your own.

## 🖼️ Preview

### Themes

<table>
  <tr>
    <td align="center"><img src="https://github.com/user-attachments/assets/b7abf0ff-08a1-4a8c-a9e3-8d0a8b89bc72" width="160" alt="Sakura"/><br/>🌸 Sakura</td>
    <td align="center"><img src="https://github.com/user-attachments/assets/f38f0ec0-9ca6-4c68-8224-ddb1b1d4cfcf" width="160" alt="Matcha"/><br/>🍵 Matcha</td>
    <td align="center"><img src="https://github.com/user-attachments/assets/033ef4e7-d1b6-4297-baf6-b10909c09ec4" width="160" alt="Lavender"/><br/>💜 Lavender</td>
  </tr>
  <tr>
    <td align="center"><img src="https://github.com/user-attachments/assets/2b3ad9cc-5863-4daf-af1c-67d6b3f98a3d" width="160" alt="Peach"/><br/>🍑 Peach</td>
    <td align="center"><img src="https://github.com/user-attachments/assets/2d499563-d357-4bfc-b45f-6086a689e719" width="160" alt="Midnight"/><br/>🌙 Midnight</td>
    <td align="center"><img src="https://github.com/user-attachments/assets/11f76463-65b9-4da6-ac36-a538426097f7" width="160" alt="Settings"/><br/>⚙️ Settings</td>
  </tr>
</table>
=======
A cute and aesthetic Pomodoro timer desktop app built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). It features multiple timer modes, pastel themes, desktop notifications, sounds, and daily statistics.
>>>>>>> 73017273c35708727e8ed7df461f33fe5252dac7

## ✨ Features

* **Three modes**: Focus, Break, and Long Break.
* **5 themes**: 🌸 Sakura, 🍵 Matcha, 💜 Lavender, 🍑 Peach, 🌙 Midnight.
* **Auto cycle**: After 4 focus sessions, the app automatically switches to a long break.
* **Auto start**: Automatically start the next break or focus session.
* **Custom alarm**: Supports your own `.wav` sound.
* **Desktop notifications** when a session ends.
* **Daily statistics** for completed Pomodoros and total focus time.
* **Persistent settings** for durations, auto start, and theme.
* **GIF support** with optional local animations.
* **Fallback emoji** when no GIF is available.

## 📦 Requirements

* Windows
* Python 3.8 or newer
* `customtkinter`
* `pillow`
* `plyer`

> The application uses Windows' built-in `winsound` module for alarm sounds.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/amirsr43/Pomodoro-Timer.git
cd Pomodoro-Timer
```

### 2. Install dependencies

```bash
pip install customtkinter pillow plyer
```

<<<<<<< HEAD
# 3. run it
python app.py
=======
### 3. Run the application

```bash
python main.py
>>>>>>> 73017273c35708727e8ed7df461f33fe5252dac7
```

## 🎮 How to Use

1. Choose a mode: **Focus**, **Break**, or **Long Break**.
2. Press **Start** to begin the timer.
3. Use **Pause** to temporarily stop the timer.
4. Use **Reset** to restart the current timer.
5. Open **⚙ Settings** to customize durations, auto start, and theme.
6. When a session ends, an alarm and desktop notification will appear.
7. After 4 completed focus sessions, the app switches to a long break.

The four dots below the timer show your progress toward the next long break.

## 🎨 Customization

### Durations and Auto Start

Open **⚙ Settings** to change:

* Focus duration
* Short break duration
* Long break duration
* Auto start break
* Auto start focus
* Theme

Default durations:

```text
Focus:      25 minutes
Break:       5 minutes
Long Break: 15 minutes
```

### GIFs

<<<<<<< HEAD
At the top of `config.py`, edit `GIF_SOURCES`. Each entry can be a **direct link** to a `.gif` or a **file name** inside `assets/`:
=======
GIFs are optional. To use a local GIF, place it inside the `assets/` folder and update `GIF_SOURCES` in `main.py`:
>>>>>>> 73017273c35708727e8ed7df461f33fe5252dac7

```python
GIF_SOURCES = {
    "idle": "idle.gif",
    "focus": "focus.gif",
    "break": "break.gif",
    "long_break": "long_break.gif"
}
```

If a GIF is unavailable, the application automatically displays a fallback emoji.

> GIF files are not included in this repository by default.

<<<<<<< HEAD
Put a file named `alarm.wav` in `assets/`, or change `ALARM_SOUND_FILE` in `config.py`. It can be a file name or a full path:
=======
### Alarm Sound
>>>>>>> 73017273c35708727e8ed7df461f33fe5252dac7

You can use a custom `.wav` sound by placing `alarm.wav` inside the `assets/` folder.

```text
assets/
└── alarm.wav
```

If no custom sound is available, the application uses a default Windows beep.

### Themes

<<<<<<< HEAD
Add a new entry to the `THEMES` dictionary in `config.py` and its color dot appears in the header automatically:
=======
The application includes five built-in themes:
>>>>>>> 73017273c35708727e8ed7df461f33fe5252dac7

* 🌸 Sakura
* 🍵 Matcha
* 💜 Lavender
* 🍑 Peach
* 🌙 Midnight

Themes can be customized by editing the `THEMES` dictionary in `main.py`.

## 💾 Application Data

User settings and daily statistics are automatically saved in the Windows AppData folder:

```text
%APPDATA%\pomo\
├── settings.json
├── stats.json
└── cache/
```

These files are created automatically when the application runs.

They are **not stored inside the project directory or GitHub repository**.

## 🗂️ Project Structure

```text
Pomodoro-Timer/
<<<<<<< HEAD
├── app.py                   # entry point
├── config.py                # constants, themes, GIF sources
├── data.py                  # load/save settings & stats
├── gif_player.py            # animated GIF player
├── sound.py                 # alarm sound & notifications
├── timer.py                 # timer state & logic
├── ui/
│   ├── app_window.py        # all widgets + display + theme
│   └── settings_window.py   # settings & error dialogs
└── assets/
    ├── alarm.wav            # optional custom alarm
    ├── tampilan/            # theme & settings screenshots
    └── cache/               # downloaded GIFs (auto-created)
=======
├── assets/          # optional local assets
├── main.py          # main application
├── .gitignore
└── README.md
>>>>>>> 73017273c35708727e8ed7df461f33fe5252dac7
```

## 🔒 Privacy

The application does not require an account and does not store application settings inside the project folder.

Local settings and statistics are stored on the user's own Windows computer under `%APPDATA%\pomo`.

## 📝 Notes

* This application is currently designed for Windows.
* GIFs and custom alarm sounds are optional.
* Local GIF and sound files are not included in this repository.
* Application data such as settings and statistics is generated automatically at runtime.

## 📄 License

This project is free to use and modify.

If you plan to redistribute or publish modified versions, make sure any third-party assets you add comply with their respective licenses.

---

<div align="center">

Made with 🍅 and Python

</div>
