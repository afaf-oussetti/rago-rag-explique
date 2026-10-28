"""Interface en ligne de commande : `python -m rago build s01e01`."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from rago import __version__

DEFAULT_EPISODES_DIR = Path("episodes")


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

    return 0
