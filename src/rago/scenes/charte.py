"""Planches de la charte graphique : un exemple d'écran et les expressions de Rago."""

from __future__ import annotations

from pathlib import Path

from manim import DOWN, LEFT, RIGHT, UP, DashedLine, Rectangle, Scene, VGroup

from rago import theme
from rago.character import EXPRESSIONS, Rago
from rago.components import (
    concept_arrow,
    document_icon,
    episode_tag,
    rago_text,
    signature,
    subtitle,
)
from rago.scenes.base import render_still


def _safe_zone_overlay() -> VGroup:
    """Hachure les zones recouvertes par Instagram (uniquement pour la planche de charte)."""
    half_w, half_h = theme.FRAME_WIDTH / 2, theme.FRAME_HEIGHT / 2
    group = VGroup()
    for y_edge, y_limit in ((half_h, theme.SAFE_TOP_Y), (-half_h, theme.SAFE_BOTTOM_Y)):
        zone = Rectangle(width=theme.FRAME_WIDTH, height=abs(y_edge - y_limit), stroke_width=0)
        zone.set_fill(theme.TEXT_MUTED, 0.12).move_to(UP * (y_edge + y_limit) / 2)
        limit = DashedLine(LEFT * half_w + UP * y_limit, RIGHT * half_w + UP * y_limit)
        limit.set_stroke(theme.TEXT_MUTED, 3, opacity=0.6)
        label = rago_text("zone recouverte par Instagram", size=18, color=theme.TEXT_MUTED)
        group.add(zone, limit, label.move_to(zone))
    return group


class CharteEcran(Scene):
    """Exemple d'écran d'épisode : titre, Rago, concept animé, sous-titre et signature."""

    def construct(self) -> None:
        """Compose l'écran d'exemple."""
        rago = Rago("perdu").scale(0.85).move_to(LEFT * 1.6 + UP * 0.6)
        doc = document_icon().move_to(RIGHT * 2.6 + UP * 2.4)
        doc_label = rago_text("Source fiable", size=24, color=theme.TRUTH, weight="MEDIUM")
        doc_label.next_to(doc, DOWN, buff=0.25)
        bubble = rago_text("1972 ?!", size=48, color=theme.HALLUCINATION, weight="BOLD")
        bubble.next_to(rago.bulb, RIGHT, buff=0.4)

        self.add(
            _safe_zone_overlay(),
            episode_tag("S01E01", "L'hallucination"),
            rago,
            bubble,
            doc,
            doc_label,
            concept_arrow(doc, rago.head),
            subtitle('Je devine le mot le plus <span foreground="#FF9F1C">probable</span>.'),
            signature(),
        )


class CharteExpressions(Scene):
    """Planche des expressions de Rago, de la palette et de la police."""

    def construct(self) -> None:
        """Compose la planche des expressions."""
        title = rago_text("Les expressions de Rago", size=44, weight="BOLD")
        title.move_to(UP * (theme.SAFE_TOP_Y - 0.5))

        cells = VGroup()
        for name, spec in EXPRESSIONS.items():
            rago = Rago(name).scale(0.5)
            label = rago_text(spec.label, size=24, color=theme.TEXT_MUTED, weight="MEDIUM")
            cells.add(VGroup(rago, label.next_to(rago, DOWN, buff=0.2)))
        top_row = VGroup(*cells[:4]).arrange(RIGHT, buff=0.35)
        bottom_row = VGroup(*cells[4:]).arrange(RIGHT, buff=0.55)
        grid = VGroup(top_row, bottom_row).arrange(DOWN, buff=0.5)
        grid.next_to(title, DOWN, buff=0.6)

        swatches = VGroup()
        for name, color in theme.PALETTE.items():
            dot = (
                Rectangle(width=0.9, height=0.9, stroke_width=3)
                .round_corners(0.2)
                .set_fill(color, 1)
                .set_stroke(theme.TEXT_MUTED, opacity=0.5)
            )
            label = rago_text(name, size=15, color=theme.TEXT_MUTED)
            swatches.add(VGroup(dot, label.next_to(dot, DOWN, buff=0.15)))
        swatches.arrange(RIGHT, buff=0.22, aligned_edge=UP).next_to(grid, DOWN, buff=0.7)

        font_sample = rago_text("Police Fredoka · Aa Bb Cc 123", size=28)
        font_sample.next_to(swatches, DOWN, buff=0.5)

        sign = signature().next_to(font_sample, DOWN, buff=0.6)

        self.add(title, grid, swatches, font_sample, sign)


CHARTE_SCENES: dict[str, type[Scene]] = {
    "charte_ecran": CharteEcran,
    "charte_expressions": CharteExpressions,
}


def render_charte(output_dir: Path) -> list[Path]:
    """Rend toutes les planches de la charte dans ``output_dir`` et renvoie leurs chemins."""
    return [render_still(cls, output_dir / f"{name}.png") for name, cls in CHARTE_SCENES.items()]
