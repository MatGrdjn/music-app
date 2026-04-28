import vlc

class PlaybackManager:

    def __init__(self):
        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()

    def play(self, source: str) -> None:
        """source : chemin local ou url de stream"""
    
        media = self._instance.media_new(source)
        self._player.set_media(media)
        self._player.play()

    def resume(self) -> None:
        self._player.set_pause(0)
    
    def pause(self) -> None:
        self._player.set_pause(1)
    
    def stop(self) -> None:
        self._player.stop()
    
    def seek(self, position: float) -> None:
        """Position entre 0.0 et 1.0"""

        self._player.set_position(position)
    
    def get_position(self) -> float:
        return self._player.get_position()
    
    def get_duration(self) -> int:
        """Durée en milliseconde"""

        return self._player.get_length()
    
    def is_playing(self) -> bool:
        return self._player.is_playing() == 1