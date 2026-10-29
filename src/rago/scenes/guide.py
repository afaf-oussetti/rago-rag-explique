"""Illustrations propres au guide PDF : la couverture et le schéma « Le RAG en une page »."""

from __future__ import annotations

from manim import DOWN, LEFT, RIGHT, UP, Arrow, Circle, RoundedRectangle, Scene, VGroup

from rago import theme
from rago.character import Rago
from rago.components import (
    book,
    check_mark,
    document_icon,
    magnifier,
    rago_text,
    speech_bubble,
)


class CouvertureGuide(Scene):
    """Rago tout content, entouré de documents et de livres."""

    def construct(self) -> None:
        """Compose l'illustration de couverture."""
        rago = Rago("excite").scale(1.1)
        props = VGroup(
            document_icon().scale(0.8).rotate(0.25).move_to(LEFT * 3.0 + UP * 2.2),
            book(color=theme.ACCENT, title="RAG")
            .scale(0.8)
            .rotate(-0.2)
            .move_to(RIGHT * 3.0 + UP * 2.0),
            document_icon().scale(0.7).rotate(-0.3).move_to(LEFT * 3.1 + DOWN * 1.6),
            book(color=theme.TRUTH).scale(0.7).rotate(0.15).move_to(RIGHT * 3.1 + DOWN * 1.7),
        )
        self.add(props, rago)


def _step_badge(number: int, name: str) -> VGroup:
    disc = Circle(radius=0.32, stroke_width=0).set_fill(theme.ACCENT, 1)
    digit = rago_text(str(number), size=30, color=theme.BACKGROUND, weight="BOLD").move_to(disc)
    label = rago_text(name, size=30, color=theme.ACCENT, weight="BOLD")
    return VGroup(VGroup(disc, digit), label).arrange(RIGHT, buff=0.2)


class SchemaRag(Scene):
    """Le RAG en une image : question → récupérer → augmenter → générer."""

    def construct(self) -> None:
        """Compose le schéma, du haut vers le bas."""
        question = speech_bubble("Quand a été construite la tour Eiffel ?", size=26)

        docs = VGroup(*(document_icon().scale(0.55) for _ in range(4))).arrange(RIGHT, buff=0.3)
        found = docs[1]
        highlight = RoundedRectangle(
            width=found.width + 0.2, height=found.height + 0.2, corner_radius=0.15
        ).set_stroke(theme.TRUTH, 8)
        highlight.move_to(found)
        loupe = magnifier().scale(0.8).move_to(found.get_corner(DOWN + RIGHT) + RIGHT * 0.1)
        retrieve = VGroup(_step_badge(1, "Récupérer"), VGroup(docs, highlight, loupe)).arrange(
            DOWN, buff=0.35
        )

        prompt_lines = VGroup(
            rago_text("Question : quand a été construite… ?", size=22),
            rago_text("Document 1 : « …achevée en 1889… »", size=22, color=theme.TRUTH),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        card = RoundedRectangle(
            width=prompt_lines.width + 0.7, height=prompt_lines.height + 0.6, corner_radius=0.25
        )
        card.set_fill(theme.RAGO_SCREEN, 1).set_stroke(theme.ACCENT, 4)
        augment = VGroup(
            _step_badge(2, "Augmenter"), VGroup(card, prompt_lines.move_to(card))
        ).arrange(DOWN, buff=0.35)

        rago = Rago("content").scale(0.45)
        answer = speech_bubble("En 1889, d'après le document 1.", color=theme.TRUTH, size=24)
        tick = check_mark(size=0.5)
        generate = VGroup(
            _step_badge(3, "Générer"),
            VGroup(rago, VGroup(answer, tick).arrange(RIGHT, buff=0.2)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, buff=0.35)

        steps = VGroup(question, retrieve, augment, generate).arrange(DOWN, buff=0.9)
        steps.scale_to_fit_height(min(steps.height, theme.FRAME_HEIGHT - 1.0)).move_to(UP * 0)
        arrows = VGroup(
            *(
                Arrow(
                    upper.get_bottom(),
                    lower.get_top(),
                    buff=0.12,
                    stroke_width=8,
                    color=theme.ACCENT,
                )
                for upper, lower in zip(steps[:-1], steps[1:], strict=True)
            )
        )
        self.add(steps, arrows)
