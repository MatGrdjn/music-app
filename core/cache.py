import time
from pathlib import Path
from data.interface import StorageInterface, Track


class CacheEngine:

    def __init__(self, storage: StorageInterface, max_tracks: int = 50, max_age_days: int = 7):
        self._storage = storage
        self._max_tracks = max_tracks
        self._max_age_seconds = max_age_days * 24 * 3600

    def clean(self) -> list[str]:
        """Applique les règles d'éviction et retourne les yt_id supprimés"""

        tracks = self._storage.get_downloaded_tracks()
        to_delete = self._select_tracks_to_delete(tracks)

        for track in to_delete:
            self._delete_file(track)
            track.is_downloaded = False
            track.file_path = None
            self._storage.save_track(track)
        
        return [track.yt_id for track in to_delete]
    
    def _select_tracks_to_delete(self, tracks: list[Track]) -> list[Track]:
        now = time.time()

        # === Règle 1 : pas écouté depuis longtemps ===

        too_old = [
            track for track in tracks
            if track.last_played and (now - track.last_played) > self._max_age_seconds
        ]

        # === Règle 2 : volume dépassé ===

        remaining = [track for track in tracks if track not in too_old]
        overflow = []

        if len(remaining) > self._max_tracks:
            sorted_by_plays = sorted(remaining, key=lambda t: t.play_count, reverse=True)
            overflow = sorted_by_plays[self._max_tracks:]
        
        return too_old + overflow
    
    def _delete_file(self, track: Track) -> None:
        if track.file_path:
            path = Path(track.file_path)
            if path.exists():
                path.unlink()