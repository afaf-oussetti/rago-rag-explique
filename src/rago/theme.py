"""Constantes visuelles et de format partagées par tous les épisodes.

Ce module ne dépend pas de Manim : il ne contient que des valeurs. La charte complète
est décrite dans ``docs/CHARTE.md``.
"""

from pathlib import Path
from typing import Any, Final

# --- Format vidéo -----------------------------------------------------------------

VIDEO_WIDTH: Final = 1080
VIDEO_HEIGHT: Final = 1920
FPS: Final = 30

# Plus d'une minute : condition de rémunération TikTok (Creator Rewards), avec une marge.
EPISODE_MIN_SECONDS: Final = 62
EPISODE_MAX_SECONDS: Final = 80

# Dimensions de l'écran en unités Manim : 1 unité = 120 pixels.
FRAME_WIDTH: Final = 9.0
FRAME_HEIGHT: Final = 16.0
PX_PER_UNIT: Final = VIDEO_WIDTH / FRAME_WIDTH

# Zones recouvertes par l'interface Instagram (pseudo, légende, boutons).
SAFE_TOP_PX: Final = 250
SAFE_BOTTOM_PX: Final = 420
SAFE_TOP_Y: Final = FRAME_HEIGHT / 2 - SAFE_TOP_PX / PX_PER_UNIT
SAFE_BOTTOM_Y: Final = -FRAME_HEIGHT / 2 + SAFE_BOTTOM_PX / PX_PER_UNIT

# Position verticale des éléments récurrents (en unités Manim).
SUBTITLE_Y: Final = SAFE_BOTTOM_Y + 1.3
SIGNATURE_Y: Final = SAFE_BOTTOM_Y + 0.22

SIGNATURE: Final = "Afaf.IA"

# --- Couleurs ---------------------------------------------------------------------

BACKGROUND: Final = "#0E1A2B"  # bleu nuit
RAGO_BODY: Final = "#2EC4B6"  # turquoise
RAGO_SHADE: Final = "#1E8F86"  # turquoise foncé (contours, oreilles, jambes)
RAGO_SCREEN: Final = "#0A1220"  # écran-visage
FACE_GLOW: Final = "#A8FFF7"  # yeux et bouche lumineux
ACCENT: Final = "#FF9F1C"  # orange : titres, flèches, mots-clés
HALLUCINATION: Final = "#E056FD"  # rose-violet : invention, erreur
TRUTH: Final = "#4ADE80"  # vert : source fiable, bonne réponse
PAPER: Final = "#FFE8A3"  # jaune papier : documents, fiches
IDEA: Final = "#FFD23F"  # jaune : ampoule, idée
TEXT: Final = "#FFF8E7"  # crème : texte principal
TEXT_MUTED: Final = "#8FA3BF"  # gris-bleu : texte secondaire

PALETTE: Final[dict[str, str]] = {
    "Fond": BACKGROUND,
    "Rago": RAGO_BODY,
    "Accent": ACCENT,
    "Invention": HALLUCINATION,
    "Source fiable": TRUTH,
    "Document": PAPER,
    "Texte": TEXT,
}

# --- Typographie ------------------------------------------------------------------

ASSETS_DIR: Final = Path(__file__).resolve().parents[2] / "assets"
FONT_PATH: Final = ASSETS_DIR / "fonts" / "Fredoka.ttf"
FONT_FAMILY: Final = "Fredoka"


def manim_config() -> dict[str, Any]:
    """Renvoie la configuration Manim commune à toutes les scènes (format Reel vertical)."""
    return {
        "pixel_width": VIDEO_WIDTH,
        "pixel_height": VIDEO_HEIGHT,
        "frame_width": FRAME_WIDTH,
        "frame_height": FRAME_HEIGHT,
        "frame_rate": FPS,
        "background_color": BACKGROUND,
    }
