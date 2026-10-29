"""Lecture et vérification des scripts d'épisodes (fichiers YAML du dossier ``episodes/``)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SECTIONS = ("hook", "probleme", "solution", "recap", "teaser")

# Doit rester identique aux clés de ``rago.character.EXPRESSIONS`` (vérifié par les tests).
# Ce module ne dépend pas de Manim, d'où cette liste séparée.
KNOWN_EXPRESSIONS = ("neutre", "content", "fier", "gene", "perdu", "pensif", "excite")


class ScriptError(ValueError):
    """Erreur dans un script d'épisode, avec un message lisible pour corriger le YAML."""


@dataclass(frozen=True)
class Line:
    """Une réplique de Rago."""

    section: str
    texte: str
    expression: str
    mot_cle: str | None = None
    animation: str = ""
    pause_apres: float = 0.0


@dataclass(frozen=True)
class Episode:
    """Un épisode complet : ses informations et ses répliques dans l'ordre."""

    id: str
    saison: int
    episode: int
    titre: str
    notion: str
    lines: tuple[Line, ...]

    @property
    def code(self) -> str:
        """Code affiché à l'écran, par exemple ``S01E01``."""
        return self.id.upper()


def _require(data: dict[str, Any], key: str, where: str) -> Any:
    if key not in data or data[key] in (None, ""):
        raise ScriptError(f"{where} : le champ « {key} » est obligatoire.")
    return data[key]


def _parse_line(data: Any, number: int) -> Line:
    where = f"Réplique {number}"
    if not isinstance(data, dict):
        raise ScriptError(
            f"{where} : une réplique doit être une liste de champs (section, texte...)."
        )

    section = _require(data, "section", where)
    if section not in SECTIONS:
        raise ScriptError(
            f"{where} : section « {section} » inconnue. Possibles : {', '.join(SECTIONS)}"
        )

    expression = _require(data, "expression", where)
    if expression not in KNOWN_EXPRESSIONS:
        known = ", ".join(KNOWN_EXPRESSIONS)
        raise ScriptError(f"{where} : expression « {expression} » inconnue. Possibles : {known}")

    texte = str(_require(data, "texte", where)).strip()
    mot_cle = data.get("mot_cle")
    if mot_cle is not None and str(mot_cle).lower() not in texte.lower():
        raise ScriptError(f"{where} : le mot-clé « {mot_cle} » n'apparaît pas dans le texte.")

    try:
        pause = float(data.get("pause_apres", 0.0))
    except (TypeError, ValueError):
        raise ScriptError(f"{where} : « pause_apres » doit être un nombre de secondes.") from None
    if pause < 0:
        raise ScriptError(f"{where} : « pause_apres » ne peut pas être négative.")

    return Line(
        section=section,
        texte=texte,
        expression=expression,
        mot_cle=str(mot_cle) if mot_cle is not None else None,
        animation=str(data.get("animation", "")).strip(),
        pause_apres=pause,
    )


def parse_episode(data: Any) -> Episode:
    """Transforme le contenu YAML déjà chargé en ``Episode`` vérifié.

    Raises:
        ScriptError: si un champ manque ou contient une valeur inconnue.
    """
    if not isinstance(data, dict):
        raise ScriptError("Le script doit commencer par les champs id, saison, episode, titre...")

    lines_data = _require(data, "repliques", "Épisode")
    if not isinstance(lines_data, list):
        raise ScriptError("Épisode : « repliques » doit être une liste.")

    return Episode(
        id=str(_require(data, "id", "Épisode")).lower(),
        saison=int(_require(data, "saison", "Épisode")),
        episode=int(_require(data, "episode", "Épisode")),
        titre=str(_require(data, "titre", "Épisode")),
        notion=str(_require(data, "notion", "Épisode")),
        lines=tuple(_parse_line(line, number) for number, line in enumerate(lines_data, start=1)),
    )


def load_episode(path: Path) -> Episode:
    """Lit et vérifie le script YAML d'un épisode.

    Args:
        path: Chemin du fichier ``episodes/<id>_<titre>.yaml``.

    Raises:
        ScriptError: si le fichier est invalide.
    """
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ScriptError(f"{path.name} : YAML invalide ({error}).") from error
    return parse_episode(data)
