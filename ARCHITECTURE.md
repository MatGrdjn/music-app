Voici une proposition de document de conception complet au format Markdown pour ton projet. Ce document détaille l'architecture, la logique métier et la structure technique pour assurer une base solide et évolutive.

---

# Architecture du Projet : PyMusicStreamer

Ce document décrit la conception d'une application de streaming de musique légère avec mise en cache intelligente, développée en Python avec **CustomTkinter** pour l'interface graphique, **VLC** pour le moteur audio et **ytmusicapi** pour l'accès aux données.

## 1. Stack Technique
* **Gestionnaire de projet :** `uv` (ultra-rapide, gestion des environnements virtuels simplifiée).
* **Source de données :** `ytmusicapi` (YouTube Music).
* **Téléchargement :** `yt-dlp` (backend pour récupérer les flux audio).
* **Interface Graphique (GUI) :** `CustomTkinter` (Look moderne pour Python).
* **Moteur Audio :** `python-vlc` (Robuste, supporte de nombreux formats).
* **Persistance initiale :** Fichier CSV (via une interface de stockage abstraite).

---

## 2. Architecture Logicielle

L'application repose sur une séparation claire entre l'interface utilisateur (UI), le moteur de lecture (Player) et le gestionnaire de données (Storage).



### Modules principaux :
1.  **`StorageManager` (Interface) :** Une classe abstraite définissant les méthodes `save_track`, `get_track_stats`, `update_play_count`, etc.
    * *Implémentation 1 :* `CSVStorage` (Actuelle).
    * *Implémentation 2 :* `SQLiteStorage` (Future).
2.  **`CacheEngine` :** Gère la logique d'éviction des fichiers ($x$ musiques, temps $y$).
3.  **`BackgroundDownloader` :** Gère la file d'attente des téléchargements de manière asynchrone (Thread dédié).
4.  **`PlaybackManager` :** Pilote l'instance VLC et gère les transitions entre les morceaux.

---

## 3. Logique du Cache et Pré-chargement

### Algorithme de nettoyage du cache
Le cache est évalué à chaque fin de morceau ou au démarrage de l'application :
1.  **Condition Temporelle ($y$) :** On supprime l'entrée si `current_time - last_played_at > y`.
2.  **Condition de Volume ($x$) :** Si le nombre de fichiers restants > $x$, on trie par `play_count` décroissant et on supprime les fichiers les moins écoutés au-delà du rang $x$.

### Pré-chargement (Look-ahead)
Dès qu'un titre commence à jouer dans une liste de lecture :
* Le système identifie les $m$ titres suivants.
* Il vérifie s'ils sont déjà présents physiquement dans le dossier `/cache`.
* S'ils manquent, ils sont ajoutés à la file d'attente du `BackgroundDownloader`.

---

## 4. Structure de Données (CSV / DB)

Pour permettre la modularité, les deux systèmes de stockage partageront les mêmes champs :

| Champ | Description |
| :--- | :--- |
| `yt_id` | ID unique YouTube Music. |
| `title` | Titre de la chanson. |
| `artist` | Nom de l'artiste. |
| `file_path` | Chemin vers le fichier local (si téléchargé). |
| `last_played` | Horodatage de la dernière lecture. |
| `play_count` | Nombre total d'écoutes. |
| `is_downloaded` | Booléen (0 ou 1). |

---

## 5. Structure du Projet

```text
pymusic_app/
├── pyproject.toml         # Géré par uv
├── main.py                # Point d'entrée de l'application
├── core/
│   ├── __init__.py
│   ├── player.py          # Wrapper autour de VLC
│   ├── downloader.py      # Logique yt-dlp
│   └── cache.py           # Logique de nettoyage x/y
├── data/
│   ├── __init__.py
│   ├── interface.py       # Classe abstraite de stockage
│   ├── csv_storage.py     # Implémentation CSV
│   └── sqlite_storage.py  # (Future implémentation)
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # Fenêtre CustomTkinter
│   └── components.py      # Boutons, barres de progression
└── music_cache/           # Dossier de stockage des .mp3/.webm
```

---

## 6. Guide d'implémentation (Code snippets)

### Définition de l'interface de stockage
```python
from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def update_track_stats(self, track_id: str):
        pass

    @abstractmethod
    def get_tracks_to_delete(self, limit_x: int, time_y_seconds: int):
        pass
```

### Initialisation avec `uv`
Pour configurer l'environnement :
```bash
uv init
uv add ytmusicapi yt-dlp python-vlc customtkinter
```

### Le gestionnaire de téléchargement en arrière-plan
Utilisation de `threading.Thread` et `queue.Queue` pour ne pas bloquer l'interface `CustomTkinter` pendant les téléchargements de $m$ sons.

---

## 7. Prochaines Étapes
1.  **Phase 1 :** Créer le `CSVStorage` et le wrapper `ytmusicapi` pour la recherche.
2.  **Phase 2 :** Implémenter le `PlaybackManager` avec VLC (Play/Pause/Next).
3.  **Phase 3 :** Ajouter le `BackgroundDownloader` et la logique de pré-chargement $m$.
4.  **Phase 4 :** Développer l'interface graphique avec `CustomTkinter`.
5.  **Phase 5 :** Implémenter la logique de nettoyage du cache $x, y$.