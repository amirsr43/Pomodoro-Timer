import os
import hashlib
import threading
import urllib.request

import customtkinter as ctk
from PIL import Image, ImageOps, ImageSequence

from config import GIF_SOURCES, GIF_FALLBACK, CACHE_DIR, ASSETS_DIR, FONT


class GifPlayer:
    def __init__(self, parent, size):
        self.size        = size
        self.cache       = {}
        self.frames      = []
        self.delays      = []
        self.index       = 0
        self.job         = None
        self.current     = None
        self.downloading = set()
        self.failed      = set()

        # gambar transparan buat placeholder kalau GIF tidak ada
        blank      = Image.new("RGBA", size, (0, 0, 0, 0))
        self.blank = ctk.CTkImage(blank, size=size)

        self.label = ctk.CTkLabel(
            parent,
            text="",
            image=self.blank,
            width=size[0],
            height=size[1],
            font=(FONT, 64),
        )

    # ── private ────────────────────────────────────────────────────────────────

    def _download(self, url: str, path: str) -> None:
        """Download GIF di background thread agar UI tidak freeze."""
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)

            request = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
            )

            with urllib.request.urlopen(request, timeout=15) as response:
                data = response.read()

            temp_path = path + ".part"

            with open(temp_path, "wb") as f:
                f.write(data)

            os.replace(temp_path, path)

        except Exception:
            self.failed.add(url)

        finally:
            self.downloading.discard(url)

    def _resolve(self, key: str):
        """Return (path, url). url = None kalau source-nya file lokal."""
        source = GIF_SOURCES[key]

        if source.startswith(("http://", "https://")):
            name = hashlib.md5(source.encode()).hexdigest() + ".gif"
            return os.path.join(CACHE_DIR, name), source

        return os.path.join(ASSETS_DIR, source), None

    def _retry(self, key: str) -> None:
        self.job     = None
        self.current = None
        self.play(key)

    def _animate(self) -> None:
        self.label.configure(image=self.frames[self.index])

        if len(self.frames) == 1:
            self.job = None
            return

        delay      = self.delays[self.index]
        self.index = (self.index + 1) % len(self.frames)
        self.job   = self.label.after(delay, self._animate)

    # ── public ─────────────────────────────────────────────────────────────────

    def load(self, key: str):
        """Return (frames, delays), atau None jika masih didownload."""
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
                    daemon=True,
                ).start()

            return None

        frames, delays = [], []

        try:
            with Image.open(path) as gif:
                for frame in ImageSequence.Iterator(gif):
                    delay = frame.info.get("duration", 100)
                    img   = ImageOps.contain(frame.convert("RGBA"), self.size)

                    frames.append(ctk.CTkImage(img, size=img.size))
                    delays.append(max(20, delay))

        except (FileNotFoundError, OSError):
            frames, delays = [], []

            # link bukan file gambar (misal halaman web) → buang cache
            if url is not None and os.path.exists(path):
                os.remove(path)

        self.cache[key] = (frames, delays)
        return self.cache[key]

    def play(self, key: str) -> None:
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
            self.label.configure(image=self.blank, text=GIF_FALLBACK[key])
            self.job = self.label.after(300, lambda: self._retry(key))
            return

        self.frames, self.delays = result
        self.index = 0

        if not self.frames:
            self.label.configure(image=self.blank, text=GIF_FALLBACK[key])
            return

        self.label.configure(text="")
        self._animate()
