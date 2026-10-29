"""Scène de base commune à tous les épisodes : Rago, bandeau, calage sur la voix.

Une scène d'épisode hérite de ``EpisodeScene`` et écrit sa méthode ``story`` :

    class S01E01(EpisodeScene):
        def story(self):
            with self.line(0):              # réplique 1 : l'expression de Rago change toute seule
                self.show(tour_eiffel())    # les animations sont calées sur la voix
            with self.line(1):
                ...

À la sortie de chaque ``with``, la scène attend la fin de la réplique : l'animation reste
synchronisée avec l'audio, même si une réplique est plus longue que prévu.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from manim import DOWN, UP, FadeIn, FadeOut, Mobject, Scene, VGroup, tempconfig
from manim.utils.exceptions import EndSceneEarlyException
from PIL import Image

from rago import theme
from rago.character import Rago
from rago.components import episode_header
from rago.script import Episode
from rago.timing import Cue, Timeline

logger = logging.getLogger(__name__)

RAGO_SCALE = 0.7
RAGO_POSITION = DOWN * 0.45
STAGE_CENTER = UP * 3.1  # centre de la zone où apparaissent les concepts, au-dessus de Rago

_TALK_HEIGHT = 0.06  # amplitude du petit rebond de Rago quand il parle
_TALK_SPEED = 7.0


class EpisodeScene(Scene):
    """Scène Manim d'un épisode, calée sur le minutage de la voix.

    Args:
        episode: Le script de l'épisode.
        timeline: Le minutage calculé à partir des durées de la voix.
        stop_after_line: Si indiqué, la scène s'arrête à la fin de cette réplique (numéro
            commençant à 0). Sert à « photographier » un moment de l'épisode pour le guide PDF.
        **kwargs: Options transmises à ``Scene``.
    """

    def __init__(
        self,
        episode: Episode,
        timeline: Timeline,
        stop_after_line: int | None = None,
        **kwargs,
    ) -> None:
        self.episode = episode
        self.timeline = timeline
        self.stop_after_line = stop_after_line
        self.stage = VGroup()
        super().__init__(**kwargs)

    def setup(self) -> None:
        """Installe le bandeau de l'épisode et Rago avant le début de l'histoire."""
        first_expression = self.episode.lines[0].expression
        self.rago = Rago(first_expression).scale(RAGO_SCALE).move_to(RAGO_POSITION)
        self.add(episode_header(self.episode.code, self.episode.titre), self.rago)

    def construct(self) -> None:
        """Joue l'histoire, puis tient la dernière image jusqu'à la fin prévue."""
        self.story()
        self.wait_until(self.timeline.total)

    def story(self) -> None:
        """Animations de l'épisode, à écrire dans chaque scène."""
        raise NotImplementedError

    # --- Calage sur la voix -------------------------------------------------------

    @property
    def now(self) -> float:
        """Temps écoulé depuis le début de la vidéo, en secondes."""
        return self.renderer.time

    def wait_until(self, time: float) -> None:
        """Attend jusqu'au moment ``time`` (ne fait rien si on y est déjà)."""
        remaining = time - self.now
        if remaining > 1 / theme.FPS:
            self.wait(remaining)

    @contextmanager
    def line(self, index: int) -> Iterator[Cue]:
        """Bloc d'une réplique : démarre avec la voix, Rago parle, puis attend la fin de la voix.

        Args:
            index: Numéro de la réplique, en commençant à 0.

        Yields:
            Le créneau de la réplique (début, durée).
        """
        if self.stop_after_line is not None and index > self.stop_after_line:
            raise EndSceneEarlyException()

        cue = self.timeline.cues[index]
        line = self.episode.lines[index]
        self.wait_until(cue.start)

        talking = _TalkingUpdater()
        self.rago.add_updater(talking)
        if line.expression != self.rago.expression:
            self.play(self.rago.animate.set_expression(line.expression), run_time=0.25)

        yield cue

        self.wait_until(cue.end)
        self.rago.remove_updater(talking)
        talking.reset(self.rago)
        if self.now > cue.end + 0.1:
            logger.warning(
                "Réplique %d : l'animation dépasse la voix de %.2f s.",
                index + 1,
                self.now - cue.end,
            )

    # --- Zone des concepts --------------------------------------------------------

    def show(self, *mobjects: Mobject, run_time: float = 0.6) -> None:
        """Fait apparaître des éléments dans la zone des concepts (ils seront effacés ensemble)."""
        self.stage.add(*mobjects)
        self.play(*(FadeIn(m, shift=UP * 0.2) for m in mobjects), run_time=run_time)

    def clear_stage(self, run_time: float = 0.4) -> None:
        """Efface tous les éléments affichés avec ``show``."""
        if len(self.stage):
            self.play(FadeOut(self.stage), run_time=run_time)
        self.stage = VGroup()


class _TalkingUpdater:
    """Petit rebond régulier de Rago pendant qu'il parle."""

    def __init__(self) -> None:
        self.time = 0.0
        self.offset = 0.0

    def __call__(self, mobject: Mobject, dt: float) -> None:
        self.time += dt
        new_offset = _TALK_HEIGHT * abs(np.sin(self.time * _TALK_SPEED))
        mobject.shift(UP * (new_offset - self.offset))
        self.offset = new_offset

    def reset(self, mobject: Mobject) -> None:
        mobject.shift(DOWN * self.offset)
        self.offset = 0.0


def render_episode_scene(
    scene_class: type[EpisodeScene], episode: Episode, timeline: Timeline, media_dir: Path
) -> Path:
    """Rend l'animation d'un épisode (sans le son) et renvoie le chemin du fichier MP4."""
    options = theme.manim_config() | {
        "media_dir": str(media_dir),
        "output_file": episode.id,
        "verbosity": "WARNING",
    }
    with tempconfig(options):
        scene = scene_class(episode=episode, timeline=timeline)
        scene.render()
        return Path(scene.renderer.file_writer.movie_file_path)


def render_line_still(
    scene_class: type[EpisodeScene],
    episode: Episode,
    timeline: Timeline,
    line_index: int,
    output_path: Path,
    media_dir: Path = Path("media"),
) -> Path:
    """Enregistre en PNG l'image de l'épisode à la fin d'une réplique, sans calculer la vidéo.

    Args:
        scene_class: La scène de l'épisode.
        episode: Le script de l'épisode.
        timeline: Le minutage de l'épisode.
        line_index: Numéro de la réplique (commençant à 0).
        output_path: Le fichier PNG à créer.
        media_dir: Le dossier de travail de Manim.

    Returns:
        Le chemin de l'image créée.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    options = theme.manim_config() | {
        "media_dir": str(media_dir),
        "save_last_frame": True,
        "write_to_movie": False,
        "disable_caching": True,
        "verbosity": "WARNING",
        "progress_bar": "none",
    }
    with tempconfig(options):
        scene = scene_class(episode=episode, timeline=timeline, stop_after_line=line_index)
        scene.render()
        Image.fromarray(scene.renderer.get_frame()).save(output_path)
    return output_path


def render_still(scene_class: type[Scene], output_path: Path) -> Path:
    """Rend une scène sans animation en image PNG au format du Reel.

    Args:
        scene_class: La scène Manim à rendre.
        output_path: Chemin du fichier PNG à créer.

    Returns:
        Le chemin de l'image créée.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    options = theme.manim_config() | {
        "media_dir": "media",
        "write_to_movie": False,
        "disable_caching": True,
        "verbosity": "WARNING",
        "progress_bar": "none",
    }
    with tempconfig(options):
        scene = scene_class()
        scene.render()
        Image.fromarray(scene.renderer.get_frame()).save(output_path)
    return output_path
