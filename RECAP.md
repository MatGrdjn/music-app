# Récap — PyMusicStreamer

## Stack technique

| Outil | Rôle |
|---|---|
| `uv` | Gestionnaire de projet et d'environnement virtuel |
| `ytmusicapi` | API non-officielle YouTube Music (recherche, métadonnées) |
| `yt-dlp` | Téléchargement de l'audio |
| `python-vlc` | Moteur de lecture audio |
| `customtkinter` | Interface graphique (à venir) |

---

## Ce qui est implémenté

### `data/interface.py` — Contrat de stockage

**Concepts abordés :** classes abstraites (`ABC`, `@abstractmethod`), dataclasses, types optionnels (`str | None`).

**`Track`** — dataclass représentant une piste :

| Champ | Type | Description |
|---|---|---|
| `yt_id` | `str` | ID unique YouTube |
| `title` | `str` | Titre |
| `artist` | `str` | Artiste |
| `file_path` | `str \| None` | Chemin local (si téléchargé) |
| `last_played` | `float \| None` | Timestamp Unix de la dernière écoute |
| `play_count` | `int` | Nombre d'écoutes |
| `is_downloaded` | `bool` | Fichier présent localement |

**`StorageInterface`** — classe abstraite définissant le contrat :

| Méthode | Rôle |
|---|---|
| `save_track(track)` | Upsert d'une piste |
| `get_track(yt_id)` | Récupère une piste par ID |
| `get_all_tracks()` | Toutes les pistes |
| `update_play_stats(yt_id, last_played)` | Incrémente `play_count`, met à jour `last_played` |
| `get_downloaded_tracks()` | Pistes avec fichier local uniquement |

---

### `data/csv_storage.py` — Stockage CSV

**Concepts abordés :** héritage, `pathlib.Path`, `csv.DictReader` / `csv.DictWriter`, pattern upsert, méthodes privées (préfixe `_`).

**Stratégie :** une ligne par piste, réécriture complète du fichier à chaque modification.

Helpers internes :
- `_read_all()` → lit le CSV, retourne une liste de `Track`
- `_write_all(tracks)` → réécrit le fichier entier
- `_track_to_row(track)` → convertit `Track` en `dict` pour le CSV
- `_row_to_track(row)` → convertit un `dict` CSV en `Track`

Interface publique : implémente les 5 méthodes de `StorageInterface`.

> **Bug à corriger :** `_write_all` utilise `csv.DictReader` au lieu de `csv.DictWriter`.
> **Bug à corriger :** `self.filepath` est assigné comme `str` mais utilisé comme `Path` — ajouter `self.filepath = Path(filepath)`.

---

### `core/player.py` — Moteur audio VLC

**Concepts abordés :** encapsulation d'une lib bas niveau, API VLC (`Instance`, `media_player_new`, `media_new`).

**Pourquoi VLC plutôt que Pygame :** VLC supporte tous les formats (webm, opus, mp3…) et les streams HTTP directement. Pygame ne supporte pas les streams ni le seek fiable.

| Méthode | Rôle |
|---|---|
| `play(source)` | Charge et joue un fichier local ou une URL |
| `resume()` | Reprend après pause (`set_pause(0)`) |
| `pause()` | Met en pause (`set_pause(1)`) |
| `stop()` | Arrête la lecture |
| `seek(position)` | Se déplace (0.0 à 1.0) |
| `get_position()` | Position actuelle (0.0 à 1.0) |
| `get_duration()` | Durée en millisecondes |
| `is_playing()` | Booléen — lecture en cours |

Note : `resume()` utilise `set_pause(0)` et non `play()`, car `play()` rechargerait le média depuis le début.

---

### `core/downloader.py` — Téléchargeur en arrière-plan

**Concepts abordés :** threading, `queue.Queue` (thread-safe), pattern worker thread, callbacks, `daemon=True`.

**Architecture :** un thread dédié tourne en boucle et pioche des IDs dans une `Queue`. Le thread principal n'est jamais bloqué.

| Méthode | Rôle |
|---|---|
| `enqueue(yt_id)` | Ajoute un ID à la file |
| `_worker()` | Boucle infinie du thread (privé) |
| `_download(yt_id)` | Télécharge via yt-dlp, retourne le chemin mp3 |

**`on_complete`** : callback optionnel appelé avec `(yt_id, file_path)` à la fin de chaque téléchargement.

Options yt-dlp : format `bestaudio`, post-traitement FFmpeg → mp3, sortie dans `music_cache/{yt_id}.mp3`.

> **Bug à corriger :** la méthode s'appelle `download` mais est appelée `self._download()` dans `_worker` — renommer en `_download`.
> **Bug à corriger :** `"format": "bestaudi/best"` → faute de frappe, doit être `"bestaudio/best"`.

---

### `core/cache.py` — Logique d'éviction du cache

**Concepts abordés :** timestamps Unix (`time.time()`), tri avec `sorted` et `lambda`, `pathlib.unlink()`.

**Deux règles d'éviction (appliquées dans l'ordre) :**

1. **Règle temporelle** : supprime les pistes dont `last_played` est plus vieux que `max_age_days` jours
2. **Règle de volume** : sur ce qui reste, garde les `max_tracks` pistes les plus écoutées, supprime le reste

Paramètres par défaut : `max_tracks=50`, `max_age_days=7`.

| Méthode | Rôle |
|---|---|
| `clean()` | Applique les règles, supprime les fichiers, met à jour le storage |
| `_select_tracks_to_delete(tracks)` | Calcule la liste à supprimer |
| `_delete_file(track)` | Supprime le fichier physique |

Après suppression : `is_downloaded = False`, `file_path = None` — la piste reste connue du storage, seul le fichier local disparaît.

---

## Ce qui reste à faire

| Phase | Module | Contenu |
|---|---|---|
| 4 | `ui/main_window.py` | Fenêtre principale CustomTkinter |
| 4 | `ui/components.py` | Boutons, barre de progression |
| — | `main.py` | Point d'entrée : instanciation et lancement de l'UI |
| (future) | `data/sqlite_storage.py` | Implémentation SQLite de `StorageInterface` |
