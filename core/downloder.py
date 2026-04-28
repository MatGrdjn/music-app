import threading
import queue
from pathlib import Path
import yt_dlp


CACHE_DIR = Path("music_cache")

class BackgroundDownloader:

    def __init__(self, on_complete=None):
        self._queue = queue.Queue()
        self._on_complete = on_complete # Appelé quand un téléchargement est terminé
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
    
    def enqueue(self, yt_id: str) -> None:
        """Ajoute un ID youtube à la file de téléchargement"""
        self._queue.put(yt_id)
    
    def _worker(self) -> None:
        """Tourne en boucle dans le thread dédié"""

        while True:
            yt_id = self._queue.get()
            
            try:
                filepath = self._download(yt_id)
                if self._on_complete:
                    self._on_complete(yt_id, filepath)
            
            finally:
                self._queue.task_done()
    
    def _download(self, yt_id: str) -> str:
        CACHE_DIR.mkdir(exist_ok=True)
        output_template = str(CACHE_DIR / f"{yt_id}.%(ext)s")

        options = {
            "format" : "bestaudio/best",
            "outtmpl" : output_template, 
            "postprocessors" : [{
                "key" : "FFmpegExtractAudio",
                "preferredcodec" : "mp3"
            }],
            "quiet" : True
        }

        url = f"https://music.youtube.com/watch?v={yt_id}"
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        
        return str(CACHE_DIR / f"{yt_id}.mp3")