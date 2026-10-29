import datetime as dt
import re
from pathlib import Path

import pytest

from rago.guide import (
    Chapter,
    GuideError,
    GuideImages,
    load_guide,
    markup,
    merge_glossary,
    parse_chapter,
    version_label,
)

ROOT = Path(__file__).resolve().parents[1]


def _chapter_data(**overrides):
    data = {
        "episode": "S09E01",
        "titre": "Test",
        "en_bref": "Un résumé.",
        "sections": [{"titre": "Partie", "texte": "Un paragraphe.", "illustration": 2}],
        "analogie": "Comme un test.",
        "a_retenir": ["Point 1", "Point 2"],
        "exercice": "Essaie !",
        "glossaire": {"Test": "Une vérification."},
    }
    data.update(overrides)
    return data


def _chapter(episode, glossaire):
    return Chapter(
        episode=episode,
        titre="T",
        sous_titre="",
        en_bref="",
        sections=(),
        analogie="",
        a_retenir=(),
        exercice="",
        glossaire=glossaire,
    )


def test_real_guide_content_is_valid():
    pages, chapters = load_guide(ROOT / "guide")
    assert chapters, "au moins un chapitre attendu"
    programme_ids = [item["id"] for item in pages["programme"]]
    for chapter in chapters:
        assert chapter.episode in programme_ids
        assert list((ROOT / "episodes").glob(f"{chapter.episode}_*.yaml")), chapter.episode


def test_parse_chapter():
    chapter = parse_chapter(_chapter_data())
    assert chapter.code == "S09E01"
    assert chapter.sections[0].paragraphes == ("Un paragraphe.",)
    assert chapter.sections[0].illustration == 2
    assert chapter.a_retenir == ("Point 1", "Point 2")


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"titre": ""}, "titre"),
        ({"sections": []}, "sections"),
        ({"sections": [{"titre": "Partie", "texte": "x", "illustration": 0}]}, "illustration"),
        ({"glossaire": ["pas", "un", "dico"]}, "glossaire"),
    ],
)
def test_invalid_chapter_is_rejected(overrides, message):
    with pytest.raises(GuideError, match=message):
        parse_chapter(_chapter_data(**overrides))


def test_glossary_is_merged_sorted_and_deduplicated():
    chapters = [
        _chapter("s01e01", {"Token": "A", "Évaluation": "B", "LLM": "C"}),
        _chapter("s01e02", {"llm": "doublon", "Embedding": "D"}),
    ]
    assert merge_glossary(chapters) == [
        ("Embedding", "D"),
        ("Évaluation", "B"),
        ("LLM", "C"),
        ("Token", "A"),
    ]


def test_markup_converts_simple_formatting_and_escapes_html():
    assert markup("**gras** & *mot* <x>", emphasis_color="#123456") == (
        '<b>gras</b> &amp; <font color="#123456">mot</font> &lt;x&gt;'
    )


def test_version_label():
    programme = [{}] * 12
    assert version_label([_chapter("s01e01", {})], programme) == "Version 1 · 1 chapitre sur 12"
    two = [_chapter("s01e01", {}), _chapter("s01e02", {})]
    assert version_label(two, programme) == "Version 2 · 2 chapitres sur 12"


def test_build_pdf_with_placeholder_images(tmp_path):
    pytest.importorskip("reportlab")
    pytest.importorskip("fontTools")
    from PIL import Image

    from rago.guide import build_pdf

    pages, chapters = load_guide(ROOT / "guide")
    placeholder = tmp_path / "image.png"
    Image.new("RGB", (400, 300), "#0E1A2B").save(placeholder)
    lines = {
        (chapter.episode, section.illustration): placeholder
        for chapter in chapters
        for section in chapter.sections
        if section.illustration is not None
    }
    images = GuideImages(cover=placeholder, schema=placeholder, lines=lines)

    output = build_pdf(pages, chapters, images, tmp_path / "guide.pdf", today=dt.date(2026, 10, 29))

    content = output.read_bytes()
    assert content.startswith(b"%PDF")
    page_count = len(re.findall(rb"/Type /Page[^s]", content))
    # 6 pages fixes (couverture, bienvenue, vue d'ensemble, programme, glossaire, suivre)
    # + au moins une page par chapitre.
    assert page_count >= 6 + len(chapters)
