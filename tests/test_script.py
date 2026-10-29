from pathlib import Path

import pytest

from rago.script import KNOWN_EXPRESSIONS, SECTIONS, ScriptError, load_episode, parse_episode

EPISODES_DIR = Path(__file__).resolve().parents[1] / "episodes"


def _episode(**line_overrides):
    line = {"section": "hook", "texte": "Bonjour à tous !", "expression": "content"}
    line.update(line_overrides)
    return {
        "id": "S09E01",
        "saison": 9,
        "episode": 1,
        "titre": "Test",
        "notion": "Les tests",
        "repliques": [line],
    }


@pytest.mark.parametrize("path", sorted(EPISODES_DIR.glob("*.yaml")), ids=lambda p: p.name)
def test_every_episode_script_is_valid(path):
    episode = load_episode(path)
    assert episode.lines
    assert path.name.startswith(episode.id)


def test_s01e01_structure():
    episode = load_episode(EPISODES_DIR / "s01e01_hallucination.yaml")
    assert episode.code == "S01E01"
    assert episode.lines[0].section == "hook"
    assert episode.lines[-1].section == "teaser"
    assert "commente rag" in episode.lines[-1].texte.lower()
    assert {line.section for line in episode.lines} == set(SECTIONS)


def test_minimal_episode_is_parsed():
    episode = parse_episode(_episode(mot_cle="Bonjour", pause_apres=0.5))
    assert episode.id == "s09e01"
    line = episode.lines[0]
    assert line.mot_cle == "Bonjour"
    assert line.pause_apres == 0.5
    assert line.animation == ""


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"section": "intro"}, "section"),
        ({"expression": "furieux"}, "expression"),
        ({"texte": ""}, "texte"),
        ({"mot_cle": "absent"}, "mot-clé"),
        ({"pause_apres": "longtemps"}, "pause_apres"),
        ({"pause_apres": -1}, "négative"),
    ],
)
def test_invalid_line_is_rejected_with_clear_message(overrides, message):
    with pytest.raises(ScriptError, match=message):
        parse_episode(_episode(**overrides))


def test_missing_episode_field_is_rejected():
    data = _episode()
    del data["titre"]
    with pytest.raises(ScriptError, match="titre"):
        parse_episode(data)


def test_invalid_yaml_is_rejected(tmp_path):
    path = tmp_path / "s09e01_casse.yaml"
    path.write_text("id: [pas fermé", encoding="utf-8")
    with pytest.raises(ScriptError, match="YAML invalide"):
        load_episode(path)


def test_known_expressions_match_character():
    pytest.importorskip("manim")
    from rago.character import EXPRESSIONS

    assert set(EXPRESSIONS) == set(KNOWN_EXPRESSIONS)
