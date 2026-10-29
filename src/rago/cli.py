"""Interface en ligne de commande : `python -m rago build s01e01`."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from rago import __version__

DEFAULT_EPISODES_DIR = Path("episodes")
DEFAULT_OUTPUT_DIR = Path("output")

# Répliques de S01E01 utilisées pour comparer les variantes de voix.
VOICE_SAMPLES = (
    "La tour Eiffel ? Facile ! Elle a été construite en 1972 par des pingouins.",
    "Quand je ne connais pas la réponse, je ne dis pas « je ne sais pas ». "
    "J'invente une phrase qui sonne juste.",
)


def find_episode_script(episode_id: str, episodes_dir: Path) -> Path | None:
    """Retrouve le script YAML d'un épisode à partir de son identifiant.

    Args:
        episode_id: Identifiant de l'épisode, par exemple ``s01e01``.
        episodes_dir: Dossier qui contient les scripts ``<id>_<titre>.yaml``.

    Returns:
        Le chemin du script, ou ``None`` s'il n'existe pas.
    """
    matches = sorted(episodes_dir.glob(f"{episode_id.lower()}_*.yaml"))
    return matches[0] if matches else None


def build_parser() -> argparse.ArgumentParser:
    """Construit l'analyseur des arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        prog="rago",
        description="Génère les épisodes de « Rago, le robot qui apprend à ne plus mentir ».",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="génère la vidéo MP4 d'un épisode")
    build.add_argument("episode", help="identifiant de l'épisode, par exemple s01e01")
    build.add_argument(
        "--episodes-dir",
        type=Path,
        default=DEFAULT_EPISODES_DIR,
        help="dossier des scripts YAML (par défaut : episodes/)",
    )

    preview = subparsers.add_parser(
        "preview", help="rend les planches de la charte graphique (PNG)"
    )
    preview.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "charte",
        help="dossier des images (par défaut : output/charte/)",
    )

    voices = subparsers.add_parser("voices", help="génère les variantes de voix de Rago (WAV)")
    voices.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "voix",
        help="dossier des fichiers audio (par défaut : output/voix/)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Lance la commande demandée et renvoie le code de sortie.

    Args:
        argv: Arguments de la ligne de commande (``sys.argv`` si ``None``).

    Returns:
        ``0`` en cas de succès, un autre code sinon.
    """
    args = build_parser().parse_args(argv)

    if args.command == "build":
        script = find_episode_script(args.episode, args.episodes_dir)
        if script is None:
            pattern = f"{args.episode}_*.yaml"
            print(f"Épisode introuvable : aucun fichier {pattern} dans {args.episodes_dir}")
            return 2
        print(f"Script trouvé : {script}")
        print("Le pipeline de génération n'est pas encore implémenté (jalon 3).")
        return 1

    if args.command == "preview":
        # Import tardif : Manim n'est nécessaire que pour cette commande.
        from rago.scenes.charte import render_charte

        for path in render_charte(args.output_dir):
            print(f"Image créée : {path}")
        return 0

    if args.command == "voices":
        from rago.voice import VOICE_PRESETS, generate_line, join_clips

        args.output_dir.mkdir(parents=True, exist_ok=True)
        for key, preset in VOICE_PRESETS.items():
            clips = [generate_line(text, preset) for text in VOICE_SAMPLES]
            output = args.output_dir / f"variante_{key}.wav"
            join_clips(clips).export(output, format="wav")
            durations = " + ".join(f"{clip.duration:.1f} s" for clip in clips)
            print(f"Variante {key} · {preset.name} ({preset.voice}) : {output} [{durations}]")
        return 0

    return 0
