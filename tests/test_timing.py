import pytest

from rago.timing import build_timeline


def test_lines_follow_each_other_with_gaps():
    timeline = build_timeline([2.0, 3.0, 1.5], lead_in=0.5, gap=0.25, tail=1.0)
    starts = [cue.start for cue in timeline.cues]
    assert starts == [0.5, 2.75, 6.0]
    assert timeline.cues[1].end == pytest.approx(5.75)
    assert timeline.total == pytest.approx(6.0 + 1.5 + 1.0)


def test_pauses_push_the_next_lines():
    without = build_timeline([2.0, 2.0], lead_in=0, gap=0)
    with_pause = build_timeline([2.0, 2.0], pauses=[1.0, 0.0], lead_in=0, gap=0)
    assert with_pause.cues[1].start == without.cues[1].start + 1.0
    assert with_pause.total == pytest.approx(without.total + 1.0)


def test_next_start_after_last_line_is_the_end():
    timeline = build_timeline([1.0, 1.0])
    assert timeline.next_start(0) == timeline.cues[1].start
    assert timeline.next_start(1) == timeline.total


def test_pauses_must_match_lines():
    with pytest.raises(ValueError):
        build_timeline([1.0, 2.0], pauses=[0.5])
