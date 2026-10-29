"""Éléments visuels réutilisables par toutes les scènes : textes, sous-titre, signature, icônes."""

from __future__ import annotations

import manimpango
from manim import (
    DL,
    DOWN,
    DR,
    LEFT,
    ORIGIN,
    PI,
    RIGHT,
    UL,
    UP,
    UR,
    Arrow,
    Circle,
    Line,
    MarkupText,
    Polygon,
    Rectangle,
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


def episode_header(code: str, title: str) -> VGroup:
    """Crée le bandeau discret affiché en haut pendant tout l'épisode : « S01E01 · titre »."""
    code_text = rago_text(code, size=20, color=theme.BACKGROUND, weight="BOLD")
    pill = RoundedRectangle(
        width=code_text.width + 0.4, height=code_text.height + 0.25, corner_radius=0.2
    ).set_fill(theme.ACCENT, 1)
    pill.set_stroke(width=0)
    badge = VGroup(pill, code_text.move_to(pill))
    title_text = rago_text(title, size=26, color=theme.TEXT, weight="MEDIUM")
    header = VGroup(badge, title_text).arrange(RIGHT, buff=0.25)
    return header.move_to(UP * (theme.SAFE_TOP_Y - 0.45))


def speech_bubble(text: str, color: str = theme.TEXT, size: float = 30) -> VGroup:
    """Crée une bulle de parole arrondie contenant un texte."""
    label = rago_text(text, size=size, color=theme.BACKGROUND, weight="MEDIUM")
    bubble = RoundedRectangle(
        width=label.width + 0.6, height=label.height + 0.5, corner_radius=0.3, stroke_width=0
    ).set_fill(color, 1)
    tail = (
        Polygon(LEFT * 0.18, RIGHT * 0.18, DOWN * 0.3 + LEFT * 0.1, stroke_width=0)
        .set_fill(color, 1)
        .next_to(bubble, DOWN, buff=-0.02)
    )
    return VGroup(bubble, tail, label.move_to(bubble))


def check_mark(color: str = theme.TRUTH, size: float = 0.6) -> VMobject:
    """Crée une coche ✓ (bonne réponse)."""
    mark = VMobject(stroke_width=14).set_stroke(color)
    mark.set_points_as_corners(
        [LEFT * 0.5 + UP * 0.05, DOWN * 0.4 + LEFT * 0.1, RIGHT * 0.55 + UP * 0.5]
    )
    return mark.scale_to_fit_width(size)


def cross_mark(color: str = theme.HALLUCINATION, size: float = 0.55) -> VGroup:
    """Crée une croix ✗ (erreur)."""
    half = size / 2
    return VGroup(
        Line(UL * half, DR * half, stroke_width=14),
        Line(UR * half, DL * half, stroke_width=14),
    ).set_stroke(color)


def book(color: str = theme.ACCENT, title: str = "") -> VGroup:
    """Crée un livre fermé, vu de face, avec un titre facultatif sur la couverture."""
    cover = RoundedRectangle(width=1.5, height=2.0, corner_radius=0.12, stroke_width=0).set_fill(
        color, 1
    )
    spine = Rectangle(width=0.18, height=2.0, stroke_width=0).set_fill(theme.BACKGROUND, 0.25)
    spine.align_to(cover, LEFT)
    group = VGroup(cover, spine)
    if title:
        label = rago_text(title, size=22, color=theme.BACKGROUND, weight="BOLD")
        group.add(label.move_to(cover).shift(RIGHT * 0.08))
    return group


def bookshelf(rows: int = 3, books_per_row: int = 7) -> VGroup:
    """Crée une bibliothèque remplie de livres colorés."""
    colors = [theme.ACCENT, theme.RAGO_BODY, theme.PAPER, theme.TRUTH, theme.IDEA, theme.TEXT_MUTED]
    frame = RoundedRectangle(width=4.6, height=1.15 * rows + 0.3, corner_radius=0.15)
    frame.set_fill(theme.RAGO_SCREEN, 1).set_stroke(theme.RAGO_SHADE, 8)
    shelves = VGroup()
    for row in range(rows):
        books = VGroup(
            *(
                Rectangle(width=0.42, height=0.8 + 0.12 * ((row + i) % 3), stroke_width=0).set_fill(
                    colors[(row * 2 + i) % len(colors)], 1
                )
                for i in range(books_per_row)
            )
        ).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        plank = Rectangle(width=4.3, height=0.08, stroke_width=0).set_fill(theme.RAGO_SHADE, 1)
        shelves.add(VGroup(books, plank.next_to(books, DOWN, buff=0)))
    shelves.arrange(DOWN, buff=0.15).move_to(frame)
    return VGroup(frame, shelves)


def phone(lines: tuple[str, ...], suggestions: tuple[str, ...]) -> VGroup:
    """Crée un téléphone avec un message en cours de saisie et la barre de suggestions."""
    body = RoundedRectangle(width=3.8, height=2.7, corner_radius=0.35).set_fill(
        theme.RAGO_SCREEN, 1
    )
    body.set_stroke(theme.TEXT_MUTED, 5)
    message = VGroup(*(rago_text(line, size=26) for line in lines)).arrange(
        DOWN, aligned_edge=LEFT, buff=0.15
    )
    message.next_to(body.get_top(), DOWN, buff=0.45).align_to(body, LEFT).shift(RIGHT * 0.3)
    chips = VGroup(
        *(
            VGroup(
                RoundedRectangle(
                    width=0.85, height=0.5, corner_radius=0.2, stroke_width=0
                ).set_fill(theme.TEXT_MUTED, 0.35),
                rago_text(word, size=20),
            )
            for word in suggestions
        )
    )
    for chip in chips:
        chip[0].stretch_to_fit_width(max(0.85, chip[1].width + 0.3))
        chip[1].move_to(chip[0])
    chips.arrange(RIGHT, buff=0.12).next_to(body.get_bottom(), UP, buff=0.35)
    return VGroup(body, message, chips)


def button(text: str, fill: str = theme.ACCENT, text_color: str = theme.BACKGROUND) -> VGroup:
    """Crée un gros bouton arrondi (appel à l'action)."""
    label = rago_text(text, size=34, color=text_color, weight="BOLD")
    pill = RoundedRectangle(
        width=label.width + 0.9, height=label.height + 0.55, corner_radius=0.4, stroke_width=0
    ).set_fill(fill, 1)
    return VGroup(pill, label.move_to(pill))


def magnifier(color: str = theme.TEXT) -> VGroup:
    """Crée une loupe (recherche dans les documents)."""
    lens = Circle(radius=0.45, stroke_width=10).set_stroke(color).set_fill(color, 0.12)
    handle = Line(ORIGIN, DR * 0.55, stroke_width=16).set_stroke(color)
    handle.shift(lens.point_at_angle(-PI / 4) - handle.get_start())
    return VGroup(lens, handle)


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
