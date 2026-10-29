"""Minutage d'un épisode : à quel moment commence et finit chaque réplique.

Le minutage est calculé à partir des durées réelles de la voix, puis partagé par
l'animation, les sous-titres et l'assemblage : tout reste synchronisé.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

LEAD_IN = 0.3  # silence avant la première réplique, en secondes
GAP = 0.6  # silence entre deux répliques
TAIL = 2.5  # temps laissé à la fin, après la dernière réplique


@dataclass(frozen=True)
class Cue:
    """Le créneau d'une réplique dans la vidéo, en secondes."""

    index: int
    start: float
    duration: float

    @property
    def end(self) -> float:
        """Fin de la réplique."""
        return self.start + self.duration


@dataclass(frozen=True)
class Timeline:
    """Le minutage complet d'un épisode."""

    cues: tuple[Cue, ...]
    total: float

    def next_start(self, index: int) -> float:
        """Début de la réplique suivante (ou fin de la vidéo après la dernière)."""
        return self.cues[index + 1].start if index + 1 < len(self.cues) else self.total


def build_timeline(
    durations: Sequence[float],
    pauses: Sequence[float] | None = None,
    lead_in: float = LEAD_IN,
    gap: float = GAP,
    tail: float = TAIL,
) -> Timeline:
    """Place les répliques les unes après les autres, séparées par un court silence.

    Args:
        durations: Durée de chaque réplique, dans l'ordre.
        pauses: Silence supplémentaire après chaque réplique (respiration), facultatif.
        lead_in: Silence avant la première réplique.
        gap: Silence entre deux répliques.
        tail: Temps laissé après la dernière réplique.

    Returns:
        Le minutage de l'épisode.
    """
    pauses = pauses or [0.0] * len(durations)
    cues = []
    time = lead_in
    for index, (duration, pause) in enumerate(zip(durations, pauses, strict=True)):
        cues.append(Cue(index=index, start=round(time, 3), duration=duration))
        time += duration + gap + pause
    total = (cues[-1].end if cues else lead_in) + tail
    return Timeline(cues=tuple(cues), total=round(total, 3))
