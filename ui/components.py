import customtkinter as ctk

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
        seconds = ms // 1000
        return f"{seconds // 60}:{seconds % 60:02d}"