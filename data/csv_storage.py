import csv
import time
from pathlib import Path
from data.interface import Track, StorageInterface

FIELDS = ["yt_id", "title", "artist", "file_path", "last_played", "play_count", "is_downloaded"]

class CSVStorage(StorageInterface):

    def __init__(self, filepath: str ="data/tracks.csv"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self._write_all([]) #Créer le fichier avec entête


    # === Helpers ===

    def _read_all(self) -> list[Track]:
        if not self.filepath.exists():
            return []

        with self.filepath.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [self._row_to_track(row) for row in reader]
    
    def _write_all(self, tracks: list[Track]) -> None:
        with self.filepath.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for track in tracks:
                writer.writerow(self._track_to_row(track))
    
    def _track_to_row(self, track: Track) -> dict:
        return {
            "yt_id": track.yt_id,
            "title": track.title,
            "artist": track.artist,
            "file_path": track.file_path or "",
            "last_played": track.last_played or "",
            "play_count": track.play_count,
            "is_downloaded": int(track.is_downloaded)
            }
    
    def _row_to_track(self, row: dict) -> Track:
        return Track(
            yt_id=row["yt_id"],
            title=row["title"],
            artist=row["artist"],
            file_path=row["file_path"] or None,
              last_played=float(row["last_played"]) if row["last_played"] else None,
            play_count=int(row["play_count"]),
            is_downloaded=bool(int(row["is_downloaded"])),
            )
    
    # === Interface publique ===

    def save_track(self, track: Track) -> None:
        tracks = self._read_all()
        for i, t in enumerate(tracks):
            if t.yt_id == track.yt_id:
                tracks[i] = track
                self._write_all(tracks)
                return
        tracks.append(track)
        self._write_all(tracks)

    def get_track(self, yt_id: str) -> Track:
        for track in self._read_all():
            if track.yt_id == yt_id:
                return track
    
    def get_all_tracks(self) -> list[Track]:
        return self._read_all()
    
    def update_play_stats(self, yt_id: str, last_played: float) -> None:
        tracks = self._read_all()

        for track in tracks:
            if track.yt_id == yt_id:
                track.play_count += 1
                track.last_played = last_played
                break
        
        self._write_all(tracks)
    
    def get_downloaded_tracks(self) -> list[Track]:
        return [track for track in self._read_all() if track.is_downloaded]