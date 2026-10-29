"""Rago dessiné en formes simples Manim, réutilisable dans toutes les scènes.

Exemple dans une scène :

    rago = Rago("perdu")
    self.add(rago)
    self.play(rago.animate.set_expression("content"))
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    PI,
    RIGHT,
    UP,
    Arc,
    Circle,
    Ellipse,
    Line,
    ParametricFunction,
    RoundedRectangle,
    Star,
    VGroup,
    VMobject,
)

from rago import theme

# Taille de l'écran-visage : les visages sont dessinés pour cette largeur.
_SCREEN_WIDTH = 2.35
_SCREEN_HEIGHT = 1.65
_SCREEN_CENTER = UP * 0.25
_BODY_CENTER = DOWN * 1.65
_FACE_STROKE = 9


# --- Briques des visages (dessinées autour de l'origine = centre de l'écran) -----


def _pill_eye(width: float = 0.32, height: float = 0.52) -> VMobject:
    return RoundedRectangle(
        width=width, height=height, corner_radius=width / 2, stroke_width=0
    ).set_fill(theme.FACE_GLOW, 1)


def _happy_eye() -> VMobject:
    return Arc(radius=0.2, start_angle=0, angle=PI, stroke_width=_FACE_STROKE).set_stroke(
        theme.FACE_GLOW
    )


def _spiral_eye() -> VMobject:
    return ParametricFunction(
        lambda t: np.array([0.018 * t * np.cos(t), 0.018 * t * np.sin(t), 0]),
        t_range=[0, 4 * PI],
        stroke_width=6,
    ).set_stroke(theme.FACE_GLOW)


def _star_eye() -> VMobject:
    return Star(n=5, outer_radius=0.26, inner_radius=0.11, stroke_width=0).set_fill(theme.IDEA, 1)


def _smile(width: float = 0.3) -> VMobject:
    return Arc(
        radius=width, start_angle=PI + 0.45, angle=PI - 0.9, stroke_width=_FACE_STROKE
    ).set_stroke(theme.FACE_GLOW)


def _grin() -> VMobject:
    return Arc(radius=0.3, start_angle=PI, angle=PI, stroke_width=0).set_fill(theme.FACE_GLOW, 1)


def _flat_mouth(width: float = 0.3) -> VMobject:
    return Line(LEFT * width / 2, RIGHT * width / 2, stroke_width=_FACE_STROKE).set_stroke(
        theme.FACE_GLOW
    )


def _wavy_mouth() -> VMobject:
    return ParametricFunction(
        lambda t: np.array([t, 0.05 * np.sin(t * 20), 0]),
        t_range=[-0.32, 0.32],
        stroke_width=7,
    ).set_stroke(theme.FACE_GLOW)


def _o_mouth() -> VMobject:
    return Circle(radius=0.12, stroke_width=7).set_stroke(theme.FACE_GLOW)


def _blush() -> VGroup:
    return VGroup(
        *(
            Ellipse(width=0.36, height=0.18, stroke_width=0)
            .set_fill(theme.HALLUCINATION, 0.5)
            .move_to([side * 0.82, -0.3, 0])
            for side in (-1, 1)
        )
    )


def _pair(make_eye: Callable[[], VMobject], offset: np.ndarray = ORIGIN) -> VGroup:
    """Place deux yeux identiques, avec un décalage commun (direction du regard)."""
    return VGroup(*(make_eye().move_to([side * 0.5, 0.12, 0] + offset) for side in (-1, 1)))


def _at_mouth(mouth: VMobject, offset: np.ndarray = ORIGIN) -> VMobject:
    return mouth.move_to(DOWN * 0.42 + offset)


# --- Expressions ------------------------------------------------------------------


@dataclass(frozen=True)
class Expression:
    """Description d'une expression : visage, couleur de l'ampoule et position des bras."""

    label: str
    face: Callable[[], VGroup]
    bulb_color: str
    arms: str = "repos"


# Les clés (sans accents) sont celles utilisées dans les scripts YAML des épisodes.
EXPRESSIONS: dict[str, Expression] = {
    "neutre": Expression(
        label="neutre",
        face=lambda: VGroup(_pair(_pill_eye), _at_mouth(_smile(0.25))),
        bulb_color=theme.FACE_GLOW,
    ),
    "content": Expression(
        label="content",
        face=lambda: VGroup(_pair(_happy_eye), _at_mouth(_smile(0.32))),
        bulb_color=theme.FACE_GLOW,
    ),
    "fier": Expression(
        label="fier",
        face=lambda: VGroup(_pair(_happy_eye, UP * 0.05), _at_mouth(_grin(), UP * 0.08)),
        bulb_color=theme.ACCENT,
        arms="hanches",
    ),
    "gene": Expression(
        label="gêné",
        face=lambda: VGroup(
            _pair(lambda: _pill_eye(0.26, 0.4), LEFT * 0.12 + DOWN * 0.05),
            _at_mouth(_wavy_mouth()),
            _blush(),
        ),
        bulb_color=theme.HALLUCINATION,
    ),
    "perdu": Expression(
        label="perdu",
        face=lambda: VGroup(_pair(_spiral_eye), _at_mouth(_o_mouth())),
        bulb_color=theme.HALLUCINATION,
    ),
    "pensif": Expression(
        label="pensif",
        face=lambda: VGroup(
            _pair(_pill_eye, RIGHT * 0.12 + UP * 0.1),
            _at_mouth(_flat_mouth(0.34).rotate(0.15), RIGHT * 0.15),
        ),
        bulb_color=theme.IDEA,
    ),
    "excite": Expression(
        label="excité",
        face=lambda: VGroup(_pair(_star_eye), _at_mouth(_grin(), UP * 0.08)),
        bulb_color=theme.IDEA,
        arms="haut",
    ),
}

# Points (épaule, coude, main) du bras droit ; le bras gauche est symétrique.
_ARM_POSES: dict[str, list[tuple[float, float]]] = {
    "repos": [(0.95, -1.25), (1.2, -1.6), (1.32, -2.0)],
    "hanches": [(0.95, -1.25), (1.42, -1.6), (0.98, -1.98)],
    "haut": [(0.95, -1.25), (1.45, -0.95), (1.85, -0.5)],
}


def _build_arms(pose: str) -> VGroup:
    arms = VGroup()
    for side in (-1, 1):
        points = [np.array([side * x, y, 0]) for x, y in _ARM_POSES[pose]]
        arm = VMobject(stroke_width=14).set_stroke(theme.RAGO_SHADE)
        arm.set_points_smoothly(points)
        hand = Circle(radius=0.17, stroke_width=0).set_fill(theme.RAGO_BODY, 1).move_to(points[-1])
        arms.add(VGroup(arm, hand))
    return arms


# --- Le personnage ----------------------------------------------------------------


class Rago(VGroup):
    """Rago, le petit robot de la série.

    Il est composé de formes simples (rectangles arrondis, cercles, arcs) et peut changer
    d'expression. Taille par défaut : environ 3 unités de large et 5 de haut.

    Args:
        expression: Nom de l'expression de départ (voir ``EXPRESSIONS``).
        **kwargs: Options transmises à ``VGroup``.
    """

    def __init__(self, expression: str = "neutre", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        spec = _get_expression(expression)
        self.expression = expression

        self.legs = VGroup(
            *(
                RoundedRectangle(width=0.42, height=0.5, corner_radius=0.18, stroke_width=0)
                .set_fill(theme.RAGO_SHADE, 1)
                .move_to([side * 0.45, -2.5, 0])
                for side in (-1, 1)
            )
        )
        self.arms = _build_arms(spec.arms)
        self.body = (
            RoundedRectangle(width=1.9, height=1.5, corner_radius=0.45, stroke_width=6)
            .set_fill(theme.RAGO_BODY, 1)
            .set_stroke(theme.RAGO_SHADE)
            .move_to(_BODY_CENTER)
        )
        self.core = Circle(radius=0.16, stroke_width=0).move_to(_BODY_CENTER + UP * 0.1)
        self.ears = VGroup(
            *(
                RoundedRectangle(width=0.3, height=0.8, corner_radius=0.12, stroke_width=0)
                .set_fill(theme.RAGO_SHADE, 1)
                .move_to([side * 1.52, 0.25, 0])
                for side in (-1, 1)
            )
        )
        self.antenna = Line(UP * 1.35, UP * 2.0, stroke_width=8).set_stroke(theme.RAGO_SHADE)
        self.bulb_glow = Circle(radius=0.36, stroke_width=0).move_to(UP * 2.15)
        self.bulb = Circle(radius=0.2, stroke_width=0).move_to(UP * 2.15)
        self.head = (
            RoundedRectangle(width=2.9, height=2.3, corner_radius=0.65, stroke_width=6)
            .set_fill(theme.RAGO_BODY, 1)
            .set_stroke(theme.RAGO_SHADE)
            .move_to(_SCREEN_CENTER)
        )
        self.screen = (
            RoundedRectangle(
                width=_SCREEN_WIDTH, height=_SCREEN_HEIGHT, corner_radius=0.45, stroke_width=0
            )
            .set_fill(theme.RAGO_SCREEN, 1)
            .move_to(_SCREEN_CENTER)
        )
        self.face = spec.face().shift(_SCREEN_CENTER)

        self.add(
            self.legs,
            self.arms,
            self.body,
            self.core,
            self.ears,
            self.antenna,
            self.bulb_glow,
            self.bulb,
            self.head,
            self.screen,
            self.face,
        )
        self._color_lights(spec.bulb_color)

    def set_expression(self, expression: str) -> Rago:
        """Change l'expression de Rago (visage, ampoule et bras), en place.

        Compatible avec ``self.play(rago.animate.set_expression("content"))``.

        Args:
            expression: Nom de l'expression (voir ``EXPRESSIONS``).

        Returns:
            Rago lui-même, pour pouvoir enchaîner les appels.
        """
        spec = _get_expression(expression)
        scale = self.screen.width / _SCREEN_WIDTH

        face = spec.face().scale(scale, about_point=ORIGIN).shift(self.screen.get_center())
        self.face.become(face)

        body_center = self.body.get_center()
        arms = _build_arms(spec.arms)
        arms.scale(scale, about_point=ORIGIN).shift(body_center - _BODY_CENTER * scale)
        self.arms.become(arms)

        self._color_lights(spec.bulb_color)
        self.expression = expression
        return self

    def _color_lights(self, color: str) -> None:
        self.bulb.set_fill(color, 1)
        self.bulb_glow.set_fill(color, 0.25)
        self.core.set_fill(color, 1)


def _get_expression(name: str) -> Expression:
    try:
        return EXPRESSIONS[name]
    except KeyError:
        known = ", ".join(EXPRESSIONS)
        raise ValueError(
            f"Expression inconnue : {name!r}. Expressions possibles : {known}"
        ) from None
