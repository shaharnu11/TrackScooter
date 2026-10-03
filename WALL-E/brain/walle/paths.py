"""Every data folder WALL-E reads or writes, in one place (all under brain/)."""

from __future__ import annotations

from pathlib import Path

BRAIN = Path(__file__).resolve().parents[1]
MODELS = BRAIN / "models"
RULES_DIR = BRAIN / "rules"
PERSONALITIES = BRAIN / "personalities"
OWNER_DIR = BRAIN / "owner"
PERSONS_DIR = BRAIN / "persons"
SPOTIFY_DIR = BRAIN / "spotify"
MUSIC_DIR = BRAIN / "music"
