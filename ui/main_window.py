import time
import customtkinter as ctk
from ytmusicapi import YTMusic

from core.player import PlaybackManager
from core.downloder import BackgroundDownloader
from core.cache import CacheEngine
from core.playlist import Playlist
from data.csv_storage import CSVStorage
from data.interface import Track
from ui.components import PlayerBar, TrackRow, PlaylistPanel


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("PyMusicStreamer")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
    
        self._storage = CSVStorage()
        self._player = PlaybackManager()
        self._downloader = BackgroundDownloader(on_complete=self._on_download_complete)
        self._cache = CacheEngine(self._storage)
        self._playlist = Playlist()
        self._ytmusic = YTMusic()
    
        self._current_track: Track | None = None
        self._search_results: list[dict] = []

        self._prefetch_done: bool = False
        self._was_playing: bool = False

        self._build()
        self._cache.clean()
        self._refresh_loop()


    def _build(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # === Ligne 0 : barre de recherche ===

        search_frame = ctk.CTkFrame(self)
        search_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=10
        )
        search_frame.columnconfigure(0, weight=1)

        self._search_entry = ctk.CTkEntry(search_frame, placeholder_text="Rechercher une chanson...")
        self._search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(10, 5), 
            pady=10
        )
        self._search_entry.bind("<Return>", lambda e : self._on_search())

        button_research = ctk.CTkButton(search_frame, text="Rechercher", width=120, command=self._on_search)
        button_research.grid(
            row=0,
            column=1,
            padx=(0, 10), 
            pady=10
        )

        # === Ligne 1 : liste des résultats et liste de lecture===

        self._result_frame = ctk.CTkScrollableFrame(self, label_text="Résultats")
        self._result_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10
        )
        self._result_frame.columnconfigure(0, weight=1)

        self._playlist_panel = PlaylistPanel(self)
        self._playlist_panel.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=10,
            pady=10
        )

        # === Ligne 2 : barre de lecture ===

        self._player_bar = PlayerBar(
            self,
            on_play_pause=self._on_play_pause,
            on_previous=self._on_previous,
            on_next=self._on_next,
            on_seek=self._on_seek
        )
        self._player_bar.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=10
        )

    

    @staticmethod
    def _extract_artist(result: dict) -> str:
        artists = result.get("artists")
        if artists and isinstance(artists, list) and len(artists) > 0:
            return artists[0].get("name", "?")
        return "?"

    def _on_search(self):
        query = self._search_entry.get().strip()
        if not query:
            return
        
        results = self._ytmusic.search(
            query=query,
            filter="songs", 
            limit=20
        )
        self._search_results = results
        self._populate_results(results)

    def _populate_results(self, results: list[dict]):
        for widget in self._result_frame.winfo_children():
            widget.destroy()
        
        for i, result in enumerate(results):
            title = result.get("title", "?")
            artist = self._extract_artist(result)

            track_row = TrackRow(self._result_frame, title, artist, on_play=lambda r=result : self._on_play_now(r), on_add=lambda r=result : self._on_add_to_queue(r))
            track_row.grid(
                row=i,
                column=0,
                sticky="ew",
                padx=5,
                pady=2
            )


    def _result_to_track(self, result: dict) -> Track:
        yt_id = result["videoId"]
        title = result.get("title", "?")
        artist = self._extract_artist(result)

        track = self._storage.get_track(yt_id)
        if track is None:
            track = Track(
                yt_id=yt_id,
                title=title,
                artist=artist,
                file_path=None,
                last_played=None,
                play_count=0,
                is_downloaded=False
            )
            self._storage.save_track(track)

        return track
    
    def _start_track(self, track: Track):
        if track.is_downloaded and track.file_path:
            self._play_track(track)
        else:
            self._downloader.enqueue(track.yt_id)

    
    def _play_track(self, track: Track):
        self._prefetch_done = False
        self._player.play(track.file_path)
        self._player_bar.set_playing(True)
        self._storage.update_play_stats(track.yt_id, time.time())

    def _refresh_playlist(self):
        tracks = self._playlist.get_tracks()
        current_index = self._playlist.get_index()

        self._playlist_panel.refresh(tracks, current_index, self._on_playlist_remove, self._on_playlist_play)

    def _on_download_complete(self, yt_id: str, file_path: str):
        track = self._storage.get_track(yt_id)
        if track:
            track.file_path = file_path
            track.is_downloaded = True
            self._storage.save_track(track)
        
        if self._current_track and self._current_track.yt_id == yt_id:
            self._current_track.file_path = file_path
            self._play_track(self._current_track)
            self._refresh_playlist()
    
    def _on_play_pause(self):
        if self._player.is_playing():
            self._player.pause()
            self._player_bar.set_playing(False)
        else:
            self._player.resume()
            self._player_bar.set_playing(True)
    
    def _on_previous(self):
        previous_track = self._playlist.previous()

        if previous_track is None:
            return

        self._current_track = previous_track
        self._player_bar.update_track_info(previous_track.title, previous_track.artist)
        self._start_track(previous_track)
        self._refresh_playlist()

    def _on_next(self):
        next_track = self._playlist.next()

        if next_track is None:
            return
        
        self._current_track = next_track
        self._player_bar.update_track_info(next_track.title, next_track.artist)
        self._start_track(next_track)
        self._refresh_playlist()

    def _on_seek(self, value: float):
        self._player.seek(value)

    def _on_play_now(self, result: dict):
        track = self._result_to_track(result)
        self._playlist.load([track])
        self._current_track = track
        self._player_bar.update_track_info(track.title, track.artist)

        self._start_track(track)
        self._refresh_playlist()

    def _on_add_to_queue(self, result: dict):
        track = self._result_to_track(result)
        self._playlist.add_next(track)
        self._refresh_playlist()

    def _on_playlist_remove(self, index: int):
        was_current = (index == self._playlist.get_index())
        self._playlist.remove(index)

        if was_current:
            self._player.stop()
            self._player_bar.set_playing(False)
            self._current_track = None
        
        self._refresh_playlist()

    def _on_playlist_play(self, index: int):
        new_track = self._playlist.jump_to(index)

        if new_track is None:
            return
        
        self._current_track = new_track
        self._player_bar.update_track_info(new_track.title, new_track.artist)
        self._start_track(new_track)
        self._refresh_playlist()
    
    def _refresh_loop(self):

        is_playing = self._player.is_playing()

        if is_playing:
            self._player_bar.update_position(
                self._player.get_duration() * self._player.get_position(), # ms écoulées
                self._player.get_duration()
            )

        if self._player.get_position() > 0.8 and self._playlist.has_next():
            
            next_track = self._playlist.peek_next()

            if next_track and not self._prefetch_done:
                self._downloader.enqueue(next_track.yt_id)
                self._prefetch_done = True

        if self._was_playing and not is_playing and self._playlist.has_next():
            self._on_next()
        

        self._was_playing = is_playing
        self.after(250, self._refresh_loop)