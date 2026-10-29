"""Sous-titres synchronisés sur la voix de Rago.

Chaque réplique est découpée en morceaux de deux lignes au plus, affichés l'un après
l'autre au rythme de la voix. Le mot-clé de la réplique est surligné en orange.
"""

from __future__ import annotations

import re
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from rago import theme
from rago.script import Line
from rago.timing import Timeline

if TYPE_CHECKING:
    from PIL import Image

MAX_CHARS_PER_LINE = 28
MAX_LINES = 2

FONT_SIZE_PX = 54
PADDING_X_PX = 36
PADDING_Y_PX = 22
LINE_SPACING_PX = 10


@dataclass(frozen=True)
class SubtitleChunk:
    """Un morceau de sous-titre affiché à l'écran pendant un créneau."""

    lines: tuple[str, ...]
    start: float
    end: float
    keywords: frozenset[str] = frozenset()

    @property
    def text(self) -> str:
        """Le texte du morceau sur une seule ligne."""
        return " ".join(self.lines)


def _normalize(word: str) -> str:
    return word.strip('.,;:!?…«»"()').lower()


def split_text(
    text: str, max_chars: int = MAX_CHARS_PER_LINE, max_lines: int = MAX_LINES
) -> list[list[str]]:
    """Découpe un texte en morceaux d'au plus ``max_lines`` lignes de ``max_chars`` caractères.

    Les coupures se font de préférence après une ponctuation, pour suivre le rythme de la phrase.

    Returns:
        La liste des morceaux, chacun étant une liste de lignes.
    """
    # Les guillemets français restent collés à leur mot : on utilise des espaces insécables.
    text = text.replace("« ", "« ").replace(" »", " »")
    clauses = [c for c in re.split(r"(?<=[.,;:!?…])\s+", text.strip()) if c]

    chunks: list[list[str]] = []
    current = ""
    for clause in clauses:
        candidate = f"{current} {clause}".strip()
        if len(textwrap.wrap(candidate, max_chars)) <= max_lines:
            current = candidate
            continue
        if current:
            chunks.append(textwrap.wrap(current, max_chars))
        wrapped = textwrap.wrap(clause, max_chars)
        while len(wrapped) > max_lines:
            chunks.append(wrapped[:max_lines])
            wrapped = wrapped[max_lines:]
        current = " ".join(wrapped)
    if current:
        chunks.append(textwrap.wrap(current, max_chars))
    return [[line.replace(" ", " ") for line in chunk] for chunk in chunks]


def build_subtitles(lines: Sequence[Line], timeline: Timeline) -> list[SubtitleChunk]:
    """Calcule tous les sous-titres d'un épisode, avec leurs horaires.

    Le temps de chaque réplique est partagé entre ses morceaux selon leur longueur. Le dernier
    morceau reste affiché jusqu'au début de la réplique suivante, pour éviter les clignotements.
    """
    subtitles = []
    for line, cue in zip(lines, timeline.cues, strict=True):
        chunks = split_text(line.texte)
        keywords = frozenset(_normalize(w) for w in (line.mot_cle or "").split())
        total_chars = sum(len(" ".join(chunk)) for chunk in chunks)
        start = cue.start
        for number, chunk in enumerate(chunks):
            share = len(" ".join(chunk)) / total_chars
            is_last = number == len(chunks) - 1
            end = timeline.next_start(cue.index) if is_last else start + share * cue.duration
            subtitles.append(SubtitleChunk(tuple(chunk), round(start, 3), round(end, 3), keywords))
            start = end
    return subtitles


def _srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def to_srt(subtitles: Sequence[SubtitleChunk]) -> str:
    """Convertit les sous-titres au format SRT (lisible par Instagram, TikTok, YouTube...)."""
    blocks = []
    for number, chunk in enumerate(subtitles, start=1):
        times = f"{_srt_time(chunk.start)} --> {_srt_time(chunk.end)}"
        blocks.append(f"{number}\n{times}\n" + "\n".join(chunk.lines))
    return "\n\n".join(blocks) + "\n"


def write_srt(subtitles: Sequence[SubtitleChunk], path: Path) -> Path:
    """Écrit le fichier ``.srt`` des sous-titres et renvoie son chemin."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_srt(subtitles), encoding="utf-8")
    return path


# --- Rendu en image (Pillow) -------------------------------------------------------


def _font(size: int, weight: str = "Medium"):
    from PIL import ImageFont

    font = ImageFont.truetype(str(theme.FONT_PATH), size)
    font.set_variation_by_name(weight)
    return font


def _hex_to_rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    color = color.lstrip("#")
    return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), alpha)


def render_chunk(chunk: SubtitleChunk) -> Image.Image:
    """Dessine un morceau de sous-titre : texte crème sur fond sombre arrondi, mot-clé en orange."""
    from PIL import Image, ImageDraw

    font = _font(FONT_SIZE_PX)
    space = font.getlength(" ")
    line_height = font.size + LINE_SPACING_PX
    widths = [font.getlength(line) for line in chunk.lines]
    width = int(max(widths) + 2 * PADDING_X_PX)
    height = int(len(chunk.lines) * line_height - LINE_SPACING_PX + 2 * PADDING_Y_PX + 8)

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (0, 0, width - 1, height - 1), radius=36, fill=_hex_to_rgba(theme.RAGO_SCREEN, 200)
    )
    y = PADDING_Y_PX
    for line, line_width in zip(chunk.lines, widths, strict=True):
        x = (width - line_width) / 2
        for word in line.split(" "):
            highlighted = _normalize(word) in chunk.keywords
            color = theme.ACCENT if highlighted else theme.TEXT
            draw.text((x, y), word, font=font, fill=_hex_to_rgba(color))
            x += font.getlength(word) + space
        y += line_height
    return image


def render_signature() -> Image.Image:
    """Dessine la signature « Afaf.IA », discrète et semi-transparente."""
    from PIL import Image, ImageDraw

    font = _font(34)
    width, height = int(font.getlength(theme.SIGNATURE)) + 8, font.size + 16
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(image).text(
        (4, 4), theme.SIGNATURE, font=font, fill=_hex_to_rgba(theme.TEXT_MUTED, 180)
    )
    return image


def y_to_pixels(y: float) -> float:
    """Convertit une hauteur Manim (0 = centre de l'écran) en pixels depuis le haut de l'image."""
    return (theme.FRAME_HEIGHT / 2 - y) * theme.PX_PER_UNIT
