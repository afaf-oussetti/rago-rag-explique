import pytest

from rago.script import Line
from rago.subtitles import MAX_CHARS_PER_LINE, MAX_LINES, build_subtitles, split_text, to_srt
from rago.timing import build_timeline

LONG = (
    "Le problème ? Quand je ne sais pas, je ne dis pas « je ne sais pas ». "
    "J'invente une réponse qui sonne juste."
)


def test_chunks_respect_line_limits():
    chunks = split_text(LONG)
    assert len(chunks) > 1
    for chunk in chunks:
        assert 1 <= len(chunk) <= MAX_LINES
        assert all(len(line) <= MAX_CHARS_PER_LINE for line in chunk)


def test_split_keeps_every_word_in_order():
    chunks = split_text(LONG)
    assert " ".join(" ".join(chunk) for chunk in chunks).split() == LONG.split()


def test_french_quotes_stay_attached_to_their_word():
    for chunk in split_text(LONG):
        for line in chunk:
            assert not line.endswith("«") and not line.startswith("»")


def test_subtitles_follow_the_voice_timing():
    lines = [
        Line(section="hook", texte="Bonjour !", expression="content"),
        Line(section="recap", texte=LONG, expression="pensif", mot_cle="J'invente"),
    ]
    timeline = build_timeline([1.0, 6.0], lead_in=0.5, gap=0.5, tail=1.0)
    subtitles = build_subtitles(lines, timeline)

    assert subtitles[0].start == 0.5
    # Le sous-titre reste affiché jusqu'à la réplique suivante, sans trou.
    assert subtitles[0].end == timeline.cues[1].start
    for previous, current in zip(subtitles, subtitles[1:], strict=False):
        assert current.start == pytest.approx(previous.end)
    assert subtitles[-1].end == timeline.total
    assert "j'invente" in subtitles[-1].keywords


def test_srt_format():
    lines = [Line(section="hook", texte="Bonjour !", expression="content")]
    timeline = build_timeline([1.25], lead_in=0.5, gap=0, tail=0)
    srt = to_srt(build_subtitles(lines, timeline))
    assert srt == "1\n00:00:00,500 --> 00:00:01,750\nBonjour !\n"
