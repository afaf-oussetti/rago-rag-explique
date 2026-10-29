"""Le pipeline complet d'un épisode : script → voix → animation → sous-titres → MP4."""

from __future__ import annotations

import importlib
from pathlib import Path

from rago import theme
from rago.script import load_episode
from rago.timing import build_timeline


def build_episode(script_path: Path, output_dir: Path, media_dir: Path = Path("media")) -> Path:
    """Génère la vidéo finale d'un épisode à partir de son script YAML.

    Args:
        script_path: Le script ``episodes/<id>_<titre>.yaml``.
        output_dir: Le dossier où écrire la vidéo et les sous-titres.
        media_dir: Le dossier de travail de Manim (fichiers intermédiaires).

    Returns:
        Le chemin de la vidéo MP4 créée.
    """
    # Imports tardifs : ces modules demandent les outils vidéo.
    from rago.assemble import assemble
    from rago.scenes.base import render_episode_scene
    from rago.subtitles import build_subtitles, write_srt
    from rago.voice import RAGO_VOICE, generate_line

    print(f"1/5 · Lecture du script {script_path.name}")
    episode = load_episode(script_path)

    print(f"2/5 · Voix de Rago ({len(episode.lines)} répliques)")
    clips = [generate_line(line.texte, RAGO_VOICE) for line in episode.lines]
    timeline = build_timeline(
        [clip.duration for clip in clips], [line.pause_apres for line in episode.lines]
    )
    print(f"      Durée de l'épisode : {timeline.total:.1f} s")
    if not theme.EPISODE_MIN_SECONDS <= timeline.total <= theme.EPISODE_MAX_SECONDS:
        print(
            f"      ⚠️  Hors de la cible {theme.EPISODE_MIN_SECONDS}-{theme.EPISODE_MAX_SECONDS} s :"
            " ajuste le texte des répliques."
        )

    print("3/5 · Animation Manim (c'est l'étape la plus longue)")
    scene_module = importlib.import_module(f"rago.scenes.{episode.id}")
    video_path = render_episode_scene(scene_module.SCENE, episode, timeline, media_dir)

    print("4/5 · Sous-titres")
    subtitles = build_subtitles(episode.lines, timeline)
    srt_path = write_srt(subtitles, output_dir / f"{episode.id}.srt")

    print("5/5 · Assemblage final")
    output_path = assemble(video_path, clips, timeline, subtitles, output_dir / f"{episode.id}.mp4")
    print(f"✅ Vidéo : {output_path}\n   Sous-titres : {srt_path}")
    return output_path
