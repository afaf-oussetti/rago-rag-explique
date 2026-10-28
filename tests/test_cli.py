from pathlib import Path

import pytest

from rago import __version__
from rago.cli import find_episode_script, main

EPISODES_DIR = Path(__file__).resolve().parents[1] / "episodes"


def test_version_is_defined():
    assert __version__


def test_help_exits_cleanly(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "build" in capsys.readouterr().out


def test_find_existing_episode():
    script = find_episode_script("S01E01", EPISODES_DIR)
    assert script is not None
    assert script.name == "s01e01_hallucination.yaml"


def test_find_missing_episode_returns_none():
    assert find_episode_script("s09e99", EPISODES_DIR) is None


def test_build_missing_episode_fails(capsys):
    code = main(["build", "s09e99", "--episodes-dir", str(EPISODES_DIR)])
    assert code == 2
    assert "introuvable" in capsys.readouterr().out
