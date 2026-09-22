import os
import threading

import winsound
from plyer import notification

from config import ASSETS_DIR, ALARM_SOUND_FILE


def resolve_sound(name: str) -> str:
    if os.path.isabs(name):
        return name
    return os.path.join(ASSETS_DIR, name)


def play_sound() -> None:
    """Putar alarm custom (.wav) kalau ada, fallback ke beep bawaan."""
    path = resolve_sound(ALARM_SOUND_FILE)

    if os.path.exists(path):
        try:
            winsound.PlaySound(
                path,
                winsound.SND_FILENAME | winsound.SND_ASYNC,
            )
            return
        except Exception:
            pass

    # fallback: beep di thread terpisah supaya animasi GIF tidak berhenti
    def beep() -> None:
        try:
            winsound.Beep(1000, 500)
            winsound.Beep(1200, 500)
        except RuntimeError:
            pass

    threading.Thread(target=beep, daemon=True).start()


def show_notification(title: str, message: str) -> None:
    try:
        notification.notify(title=title, message=message, timeout=5)
    except Exception:
        pass
