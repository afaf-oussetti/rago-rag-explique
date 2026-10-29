"""S01E01 · Rago invente des réponses : l'hallucination des LLM.

Les répliques et leurs indications sont dans ``episodes/s01e01_hallucination.yaml``.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    Ellipse,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    Line,
    MoveToTarget,
    Polygon,
    Rectangle,
    RoundedRectangle,
    Triangle,
    VGroup,
    Wiggle,
)

from rago import theme
from rago.components import (
    book,
    bookshelf,
    button,
    check_mark,
    cross_mark,
    document_icon,
    phone,
    rago_text,
    speech_bubble,
)
from rago.scenes.base import STAGE_CENTER, EpisodeScene

# --- Dessins propres à cet épisode -----------------------------------------------


def eiffel_tower() -> VGroup:
    """Une tour Eiffel stylisée, en formes simples."""
    outline = [
        (-1.0, 0), (-0.45, 1.0), (-0.22, 2.0), (-0.06, 3.2), (0, 3.6), (0.06, 3.2), (0.22, 2.0),
        (0.45, 1.0), (1.0, 0), (0.6, 0), (0.3, 0.45), (0, 0.58), (-0.3, 0.45), (-0.6, 0),
    ]  # fmt: skip
    body = Polygon(*[np.array([x, y, 0]) for x, y in outline], stroke_width=0)
    body.set_fill("#C9A27E", 1)
    platforms = VGroup(
        Rectangle(width=1.25, height=0.12, stroke_width=0).move_to(UP * 1.0),
        Rectangle(width=0.7, height=0.1, stroke_width=0).move_to(UP * 2.0),
    ).set_fill("#8C6A4F", 1)
    return VGroup(body, platforms)


def penguin() -> VGroup:
    """Un petit pingouin rigolo."""
    body = Ellipse(width=0.55, height=0.75, stroke_width=0).set_fill("#1B2235", 1)
    belly = (
        Ellipse(width=0.36, height=0.5, stroke_width=0).set_fill(theme.TEXT, 1).shift(DOWN * 0.08)
    )
    eyes = VGroup(
        *(
            Circle(radius=0.035, stroke_width=0).set_fill(theme.TEXT, 1).move_to([s * 0.09, 0.2, 0])
            for s in (-1, 1)
        )
    )
    beak = Triangle(stroke_width=0).set_fill(theme.ACCENT, 1).scale(0.06).rotate(np.pi)
    beak.move_to(UP * 0.12)
    feet = VGroup(
        *(
            Ellipse(width=0.16, height=0.07, stroke_width=0)
            .set_fill(theme.ACCENT, 1)
            .move_to([s * 0.1, -0.37, 0])
            for s in (-1, 1)
        )
    )
    return VGroup(feet, body, belly, eyes, beak)


def probability_bars(options: list[tuple[str, float, str]]) -> VGroup:
    """Mots candidats avec une barre de probabilité, comme un LLM qui choisit le mot suivant."""
    rows = VGroup()
    for word, probability, color in options:
        label = rago_text(word, size=34, weight="MEDIUM").set_color(color)
        bar = Rectangle(width=max(0.12, 3.6 * probability), height=0.42, stroke_width=0)
        bar.set_fill(color, 0.9)
        percent = rago_text(f"{round(probability * 100)} %", size=26, color=theme.TEXT_MUTED)
        rows.add(VGroup(label, bar, percent))
    labels_width = max(row[0].width for row in rows)
    for row in rows:
        label, bar, percent = row
        bar.next_to(label, RIGHT, buff=0.3 + labels_width - label.width)
        percent.next_to(bar, RIGHT, buff=0.2)
    return rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3)


# --- La scène ---------------------------------------------------------------------


class S01E01(EpisodeScene):
    """L'hallucination : Rago invente une réponse, puis découvre qu'il lui faut des sources."""

    def hide(self, *mobjects) -> None:
        """Fait disparaître certains éléments de la zone des concepts."""
        self.play(*(FadeOut(m) for m in mobjects), run_time=0.4)
        for mobject in mobjects:
            self.stage.remove(mobject)

    def story(self) -> None:
        """Les 12 répliques de l'épisode."""
        rago = self.rago

        # 1 · Hook : la bêtise
        with self.line(0):
            tower = eiffel_tower().move_to(STAGE_CENTER + RIGHT * 1.8)
            year = rago_text("1972", size=72, color=theme.HALLUCINATION, weight="BOLD")
            year.move_to(STAGE_CENTER + LEFT * 1.7 + UP * 0.5)
            self.show(tower, year, run_time=0.35)
            penguins = VGroup(*(penguin() for _ in range(3))).arrange(RIGHT, buff=0.12)
            penguins.move_to(tower.get_bottom() + UP * 0.38)
            self.stage.add(penguins)
            self.play(LaggedStart(*(GrowFromCenter(p) for p in penguins), lag_ratio=0.3))

        # 2 · La correction
        with self.line(1):
            strike = Line(year.get_left(), year.get_right(), stroke_width=10)
            strike.set_stroke(theme.HALLUCINATION)
            self.hide(penguins)
            self.stage.add(strike)
            self.play(Create(strike), run_time=0.4)
            correct = rago_text("1889", size=72, color=theme.TRUTH, weight="BOLD")
            correct.next_to(year, DOWN, buff=0.35)
            no_source = rago_text("aucune source", size=26, color=theme.HALLUCINATION)
            no_source.next_to(correct, DOWN, buff=0.3)
            self.show(correct)
            self.show(no_source, run_time=0.4)

        # 3 · Le mot le plus probable
        with self.line(2):
            self.clear_stage()
            prompt = rago_text("La tour Eiffel est à…", size=38, weight="MEDIUM")
            bars = probability_bars(
                [
                    ("Paris", 0.92, theme.TRUTH),
                    ("Rome", 0.05, theme.TEXT_MUTED),
                    ("Mars", 0.03, theme.TEXT_MUTED),
                ]
            )
            VGroup(prompt, bars).arrange(DOWN, buff=0.5).move_to(STAGE_CENTER)
            self.show(prompt)
            self.stage.add(bars)
            self.play(
                LaggedStart(
                    *(
                        LaggedStart(
                            FadeIn(row[0]),
                            GrowFromEdge(row[1], LEFT),
                            FadeIn(row[2]),
                            lag_ratio=0.3,
                        )
                        for row in bars
                    ),
                    lag_ratio=0.35,
                ),
                run_time=1.8,
            )

        # 4 · L'autocomplétion
        with self.line(3):
            self.clear_stage()
            smartphone = phone(("Je suis",), ("là", "en route", "content")).move_to(
                STAGE_CENTER + UP * 0.3
            )
            self.show(smartphone)
            self.play(Indicate(smartphone[2], color=theme.ACCENT, scale_factor=1.15), run_time=1.0)

        # 5 · Il invente
        with self.line(4):
            self.clear_stage()
            # La phrase finale est écrite d'un bloc (espacement et alignement parfaits),
            # puis découpée en mots : chaque mot part d'une position au hasard.
            rows = VGroup(
                *(
                    rago_text(text, size=40, color=theme.HALLUCINATION, weight="BOLD")
                    for text in ("Construite en 1972", "par des pingouins")
                )
            ).arrange(DOWN, buff=0.3)
            rows.move_to(STAGE_CENTER)
            pieces = VGroup()
            for row, text in zip(rows, ("Construite en 1972", "par des pingouins"), strict=True):
                position = 0
                for word in text.split():
                    pieces.add(row[position : position + len(word)].copy())
                    position += len(word)
            rng = np.random.default_rng(7)
            for piece in pieces:
                piece.generate_target()
                piece.move_to(
                    STAGE_CENTER + np.array([rng.uniform(-3, 3), rng.uniform(-1.5, 1.5), 0])
                )
                piece.rotate(rng.uniform(-0.6, 0.6))
            self.show(*pieces, run_time=0.8)
            self.wait(0.6)
            self.play(*(MoveToTarget(p) for p in pieces), run_time=1.2)

        # 6 · Une hallucination
        with self.line(5):
            self.clear_stage()
            word = rago_text("hallucination", size=64, color=theme.HALLUCINATION, weight="BOLD")
            word.move_to(STAGE_CENTER + UP * 1.1)
            self.show(word)
            lesson = book(color=theme.PAPER, title="Leçon").scale(0.8)
            closed = rago_text("jamais lue", size=26, color=theme.TEXT_MUTED)
            VGroup(lesson, closed).arrange(RIGHT, buff=0.4).move_to(STAGE_CENTER + DOWN * 0.6)
            self.wait(1.2)
            self.show(lesson, closed)

        # 7 · Même aplomb
        with self.line(6):
            self.clear_stage()
            question = rago_text(
                "Laquelle est fausse ?", size=30, color=theme.ACCENT, weight="MEDIUM"
            )
            right = speech_bubble("Elle date de 1889.", size=26)
            wrong = speech_bubble("Elle date de 1972.", size=26)
            bubbles = VGroup(right, wrong).arrange(DOWN, buff=0.35)
            VGroup(question, bubbles).arrange(DOWN, buff=0.4).move_to(STAGE_CENTER + UP * 0.2)
            self.show(question, right, wrong, run_time=0.5)
            self.wait(0.6)
            marks = VGroup(
                check_mark().next_to(right, RIGHT, buff=0.3),
                cross_mark().next_to(wrong, RIGHT, buff=0.3),
            )
            self.show(*marks, run_time=0.3)

        # 8 · Les bons documents
        with self.line(7):
            self.clear_stage()
            docs = (
                VGroup(*(document_icon() for _ in range(3)))
                .arrange(RIGHT, buff=0.45)
                .move_to(STAGE_CENTER)
            )
            checks = VGroup(
                *(check_mark(size=0.45).move_to(d.get_corner(UP + RIGHT)) for d in docs)
            )
            self.stage.add(docs, checks)
            self.play(
                LaggedStart(*(FadeIn(d, shift=LEFT * 3) for d in docs), lag_ratio=0.25),
                run_time=1.2,
            )
            self.play(
                LaggedStart(*(GrowFromCenter(c) for c in checks), lag_ratio=0.2), run_time=0.6
            )
            pile = VGroup(docs, checks)
            self.play(pile.animate.scale(0.45).next_to(rago, RIGHT, buff=0.3), run_time=0.8)

        # 9 · Le RAG
        with self.line(8):
            self.clear_stage()
            sources = document_icon().scale(0.75)
            answer = speech_bubble("C'est 1889.", color=theme.TRUTH)
            source_note = rago_text("Source : document 1", size=22, color=theme.TEXT_MUTED)
            answer_group = VGroup(answer, source_note.next_to(answer, DOWN, buff=0.2))
            (
                VGroup(sources, answer_group)
                .arrange(RIGHT, buff=1.8)
                .move_to(STAGE_CENTER + UP * 0.4)
            )
            arrow = Arrow(
                sources.get_right(),
                answer.get_left(),
                buff=0.25,
                stroke_width=10,
                color=theme.ACCENT,
            )
            self.show(sources)
            self.stage.add(arrow)
            self.play(GrowFromEdge(arrow, LEFT), run_time=0.5)
            self.show(answer_group)
            self.wait(1.0)
            self.clear_stage()
            letters = VGroup(
                *(rago_text(c, size=120, color=theme.ACCENT, weight="BOLD") for c in "RAG")
            )
            letters.arrange(RIGHT, buff=0.3).move_to(STAGE_CENTER + UP * 0.3)
            full_name = rago_text("Retrieval-Augmented Generation", size=24, color=theme.TEXT_MUTED)
            full_name.next_to(letters, DOWN, buff=0.3)
            self.stage.add(letters, full_name)
            self.play(
                LaggedStart(*(GrowFromCenter(c) for c in letters), lag_ratio=0.3), run_time=0.9
            )
            self.play(FadeIn(full_name), run_time=0.4)

        # 10 · Récap
        with self.line(9):
            self.clear_stage()
            title = rago_text("À retenir", size=34, color=theme.ACCENT, weight="BOLD")
            body = VGroup(
                *(
                    rago_text(text, size=32)
                    for text in (
                        "Un LLM sans sources,",
                        "c'est un élève qui répond",
                        "sans ouvrir le livre.",
                    )
                )
            ).arrange(DOWN, buff=0.15)
            content = VGroup(title, body).arrange(DOWN, buff=0.35)
            card = RoundedRectangle(
                width=content.width + 0.9, height=content.height + 0.8, corner_radius=0.3
            )
            card.set_fill(theme.RAGO_SCREEN, 1).set_stroke(theme.ACCENT, 5)
            recap = VGroup(card, content.move_to(card)).move_to(STAGE_CENTER)
            self.show(recap, run_time=0.7)

        # 11 · Teaser
        with self.line(10):
            self.clear_stage()
            shelf = bookshelf().scale(0.75)
            label = rago_text("Prochain épisode", size=28, color=theme.ACCENT, weight="MEDIUM")
            VGroup(label, shelf).arrange(DOWN, buff=0.3).move_to(STAGE_CENTER)
            self.show(label, shelf)

        # 12 · Appel à l'action
        with self.line(11):
            self.clear_stage()
            subscribe = button("Abonne-toi")
            comment = button("Commente RAG", fill=theme.RAGO_BODY)
            buttons = VGroup(subscribe, comment).arrange(DOWN, buff=0.45).move_to(STAGE_CENTER)
            self.show(subscribe)
            self.wait(0.8)
            self.show(comment)
            self.play(Wiggle(subscribe), run_time=0.7)
            self.play(Wiggle(comment), run_time=0.7)
            self.stage.add(buttons)


SCENE = S01E01
