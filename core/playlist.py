from data.interface import Track

class Playlist:

    def __init__(self):
        self._tracks: list[Track] = []
        self._index: int = -1


    def load(self, tracks: list[Track], start_index: int = 0) -> None:
        self._tracks = tracks
        self._index = start_index

    def current(self) -> Track | None:
        if not self._tracks or self._index < 0:
            return None
        return self._tracks[self._index]
    
    def next(self) -> Track | None:
        if self._index + 1 >= len(self._tracks):
            return None
        self._index += 1
        return self._tracks[self._index]
    
    def previous(self) -> Track | None:
        if self._index - 1 < 0:
            return None
        self._index -= 1
        return self._tracks[self._index]
    
    def has_next(self) -> bool:
        return self._index < len(self._tracks) - 1

    def has_previous(self) -> bool:
        return self._index > 0 
    
    def add_next(self, track: Track) -> None:
        if not self._tracks:
            self.load([track], start_index=0)
            return None
        
        self._tracks.insert(self._index + 1, track)

    def peek_next(self) -> Track | None:
        if self.has_next():
            return self._tracks[self._index + 1]
        
        return None