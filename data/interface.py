from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Track:
    yt_id: str 
    title: str
    artist: str
    file_path: str | None
    last_played: float | None
    play_count: int
    is_downloaded: bool


class StorageInterface(ABC):

    @abstractmethod
    def save_track(self, track: Track) -> None:
        """Enregistre ou met à jour une piste"""

    @abstractmethod
    def get_track(self, yt_id: str) -> Track | None:
        """Récupère une piste par son ID youtube"""
    
    @abstractmethod
    def get_all_tracks(self) -> list[Track]:
        """Retourne toutes les pistes connues"""
    
    @abstractmethod
    def update_play_stats(self, yt_id: str, last_played: float) -> None:
        """Incrémente le compteur et met à jour last_played"""
    
    @abstractmethod
    def get_downloaded_tracks(self) -> list[Track]:
        """Retourne uniquement les pistes téléchargées localement"""
        