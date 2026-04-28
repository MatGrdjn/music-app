import customtkinter as ctk
from data.interface import Track

class PlayerBar(ctk.CTkFrame):

    def __init__(self, parent, on_play_pause, on_previous, on_next, on_seek):
        super().__init__(parent)

        self._on_play_pause = on_play_pause
        self._on_previous = on_previous
        self._on_next = on_next
        self._on_seek = on_seek

        self._build()

    def _build(self):
        # === Ligne 0 : infos sur la piste ===

        self._label_track = ctk.CTkLabel(self, text="Aucune piste", font=ctk.CTkFont(size=13, weight="bold"))
        self._label_track.grid(
            row=0, 
            column=0, 
            columnspan=5, 
            pady=(10, 0)
            )

        # === Ligne 1 : timestamps + slider ===

        self._label_elapsed = ctk.CTkLabel(self, text="0:00", width=40)
        self._label_elapsed.grid(
            row=1, 
            column=0,
            padx=(10, 0)
        )

        self._slider = ctk.CTkSlider(self, from_=0, to=1, command=self._on_seek)
        self._slider.grid(
            row=1, 
            column=1, 
            columnspan=3, 
            sticky="ew", 
            padx=10
            )
        self._slider.set(0)

        self._label_duration = ctk.CTkLabel(self, text="0:00", width=40)
        self._label_duration.grid(
            row=1,
            column=4,
            padx=(0, 10)
        )

        # === Ligne 2 : boutons ===

        self._button_previous = ctk.CTkButton(self, text="⏮️", width=40, command=self._on_previous)
        self._button_previous.grid(
            row=2,
            column=1,
            pady=10
        )

        self._button_play = ctk.CTkButton(self, text="▶️", width=40, command=self._on_play_pause)
        self._button_play.grid(
            row=2,
            column=2,
            pady=10
        )

        self._button_next = ctk.CTkButton(self, text="⏭️", width=40, command=self._on_next)
        self._button_next.grid(
            row=2,
            column=3,
            pady=10
        )

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=1)
    

    def update_track_info(self, title: str, artist: str):
        self._label_track.configure(text=f"{title} - {artist}")
    
    def update_position(self, elapsed_ms: int, duration_ms: int):
        if duration_ms > 0:
            self._slider.set(elapsed_ms / duration_ms)
        
        self._label_elapsed.configure(text=self._ms_to_str(elapsed_ms))
        self._label_duration.configure(text=self._ms_to_str(duration_ms))
    
    def set_playing(self, is_playing: bool):
        self._button_play.configure(text="⏸️" if is_playing else "▶️")
    
    @staticmethod
    def _ms_to_str(ms: int) -> str:
        seconds = int(ms // 1000)
        return f"{seconds // 60}:{seconds % 60:02d}"
    

class TrackRow(ctk.CTkFrame):

    def __init__(self, parent, title: str, artist: str, on_play, on_add):
        super().__init__(parent)

        self._title = title
        self._artist = artist
        self._on_play = on_play
        self._on_add = on_add

        self._build()

    def _build(self):

        # === Colonne 0 : label ===

        self._label = ctk.CTkLabel(self, text=f"{self._title} - {self._artist}", anchor="w")
        self._label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(10, 5),
            pady=5
        )

        # === Colonne 1 : bouton play ===
        self._button_play = ctk.CTkButton(self, text="▶", width=36, command=self._on_play)
        self._button_play.grid(
            row=0, 
            column=1,
            padx=(0, 5),
            pady=5
        )

        # === Colonne 2 : bouton ajouter ===
        self._button_add = ctk.CTkButton(self, text="➕", width=36, command=self._on_add)
        self._button_add.grid(
            row=0,
            column=2,
            padx=(0, 10),
            pady=5
        )

        self.columnconfigure(0, weight=1)


class PlaylistRow(ctk.CTkFrame):

    def __init__(self, parent, track: Track, is_current: bool, on_remove, on_play):
        super().__init__(parent)

        self._track = track
        self._is_current = is_current
        self._on_remove = on_remove
        self._on_play = on_play

        self._build()

    def _build(self):
        text_color = "#1DB954" if self._is_current else "#FFFFFF"

        self._label_playing = ctk.CTkLabel(self, text="▶" if self._is_current else " ", text_color=text_color, width=20)
        self._label_playing.grid(
            row=0, 
            column=0, 
            padx=(10, 0), 
            pady=5
            )

        self._label_track = ctk.CTkLabel(self, text=f"{self._track.title} - {self._track.artist}", text_color=text_color, anchor="w")
        self._label_track.grid(
            row=0, 
            column=1, 
            sticky="ew", 
            padx=(5, 5), 
            pady=5
            )
        self._label_track.bind("<Button-1>", lambda e: self._on_play())

        self._button_remove = ctk.CTkButton(self, text="✕", width=30, command=self._on_remove)
        self._button_remove.grid(
            row=0, 
            column=2, 
            padx=(0, 10), 
            pady=5
            )

        self.columnconfigure(1, weight=1)


class PlaylistPanel(ctk.CTkScrollableFrame):
    
    def __init__(self, parent):
        super().__init__(parent, label="File de lecture")

        self.columnconfigure(0, weight=1)

    def refresh(self, tracks: list[Track], current_index: int, on_remove, on_play):

        for widget in self.winfo_children():
            widget.destroy()

        for i, track in enumerate(tracks):
            is_current = (i == current_index)

            playlist_row = PlaylistRow(self, track, is_current, on_remove=lambda i=i : on_remove(i), on_play=lambda i=i : on_play(i))
            playlist_row.grid(
                row=i, 
                column=0,
                sticky="ew",
                padx=5,
                pady=2
            )