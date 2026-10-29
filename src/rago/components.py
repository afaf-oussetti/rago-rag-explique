"""Éléments visuels réutilisables par toutes les scènes : textes, sous-titre, signature, icônes."""

from __future__ import annotations

import manimpango
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Line,
    MarkupText,
    RoundedRectangle,
    Text,
    VGroup,
    VMobject,
)

from rago import theme

# La police est enregistrée une fois pour toutes : Fredoka n'a pas besoin d'être
# installée sur l'ordinateur.
manimpango.register_font(str(theme.FONT_PATH))


def rago_text(text: str, size: float = 40, color: str = theme.TEXT, weight: str = "NORMAL") -> Text:
    """Crée un texte dans la police de la série.

    Args:
        text: Le texte à afficher.
        size: Taille de police, à l'échelle d'un écran 1080 pixels de large.
        color: Couleur du texte.
        weight: Graisse Pango (``"NORMAL"``, ``"MEDIUM"``, ``"BOLD"``...).
    """
    return Text(text, font=theme.FONT_FAMILY, font_size=size, color=color, weight=weight)


def subtitle(markup: str, max_width: float = theme.FRAME_WIDTH - 1.2) -> VGroup:
    """Crée un sous-titre sur fond sombre arrondi, placé dans la zone des sous-titres.

    Args:
        markup: Texte au format Pango. Pour mettre un mot en valeur :
            ``<span foreground="#FF9F1C">mot</span>``.
        max_width: Largeur maximale du texte, en unités Manim.
    """
    label = MarkupText(
        markup, font=theme.FONT_FAMILY, font_size=40, color=theme.TEXT, weight="MEDIUM"
    )
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    background = RoundedRectangle(
        width=label.width + 0.6, height=label.height + 0.45, corner_radius=0.3, stroke_width=0
    ).set_fill(theme.RAGO_SCREEN, 0.75)
    return VGroup(background, label).move_to(UP * theme.SUBTITLE_Y)


def signature() -> Text:
    """Crée la signature « Afaf.IA », discrète, en bas de l'écran."""
    return (
        rago_text(theme.SIGNATURE, size=22, color=theme.TEXT_MUTED, weight="MEDIUM")
        .set_opacity(0.7)
        .move_to(UP * theme.SIGNATURE_Y)
    )


def episode_tag(code: str, title: str) -> VGroup:
    """Crée l'étiquette d'épisode affichée en haut de l'écran, par exemple « S01E01 »."""
    code_text = rago_text(code, size=24, color=theme.BACKGROUND, weight="BOLD")
    pill = RoundedRectangle(
        width=code_text.width + 0.5, height=code_text.height + 0.35, corner_radius=0.25
    ).set_fill(theme.ACCENT, 1)
    pill.set_stroke(width=0)
    badge = VGroup(pill, code_text.move_to(pill))
    title_text = rago_text(title, size=44, weight="BOLD")
    group = VGroup(badge, title_text).arrange(DOWN, buff=0.3)
    return group.move_to(UP * (theme.SAFE_TOP_Y - group.height / 2 - 0.3))


def document_icon(color: str = theme.PAPER, lines: int = 4) -> VGroup:
    """Crée une icône de document : une feuille arrondie avec quelques lignes de texte."""
    sheet = RoundedRectangle(width=1.5, height=1.9, corner_radius=0.15, stroke_width=0).set_fill(
        color, 1
    )
    text_lines = VGroup(
        *(
            Line(LEFT * 0.5, RIGHT * (0.5 if i < lines - 1 else 0.1), stroke_width=7).set_stroke(
                theme.TEXT_MUTED
            )
            for i in range(lines)
        )
    ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
    return VGroup(sheet, text_lines.move_to(sheet))


def concept_arrow(start: VMobject, end: VMobject, color: str = theme.ACCENT) -> Arrow:
    """Crée une flèche épaisse entre deux éléments."""
    return Arrow(
        start.get_center(),
        end.get_center(),
        buff=1.0,
        stroke_width=12,
        max_tip_length_to_length_ratio=0.3,
        color=color,
    )
