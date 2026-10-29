import pytest

# Ces tests demandent pydub : ils sont ignorés si les outils vidéo ne sont pas installés.
pytest.importorskip("pydub")

from pydub import AudioSegment  # noqa: E402
from pydub.generators import Sine  # noqa: E402

from rago.voice import (  # noqa: E402
    VOICE_PRESETS,
    VoiceClip,
    add_echo,
    add_metal,
    apply_robot_effect,
    cache_key,
    join_clips,
    trim_silence,
)


def _tone(ms=1000):
    return Sine(440).to_audio_segment(duration=ms).set_frame_rate(24000).set_channels(1) - 6


def test_metal_and_echo_keep_duration():
    tone = _tone()
    assert len(add_metal(tone, mix=0.3, freq=55)) == len(tone)
    assert len(add_echo(tone, delay_ms=50, gain_db=-14)) == len(tone)


def test_effects_are_skipped_when_disabled():
    tone = _tone()
    assert add_metal(tone, mix=0, freq=55) is tone
    assert add_echo(tone, delay_ms=0, gain_db=-14) is tone


def test_metal_changes_the_sound():
    tone = _tone()
    assert add_metal(tone, mix=0.5, freq=55).raw_data != tone.raw_data


def test_trim_silence_removes_padding_but_keeps_margin():
    padded = (
        AudioSegment.silent(500, frame_rate=24000)
        + _tone(1000)
        + AudioSegment.silent(700, frame_rate=24000)
    )
    trimmed = trim_silence(padded, keep_ms=60)
    assert 1100 <= len(trimmed) <= 1150


@pytest.mark.parametrize("preset", list(VOICE_PRESETS.values()), ids=list(VOICE_PRESETS))
def test_robot_effect_keeps_speech_duration(preset):
    speech = AudioSegment.silent(300, frame_rate=24000) + _tone(1500)
    result = apply_robot_effect(speech, preset)
    assert 1500 <= len(result) <= 1600
    assert result.channels == 1


def test_cache_key_depends_on_text_and_settings():
    preset = VOICE_PRESETS["A"]
    assert cache_key("Bonjour", preset) == cache_key("  Bonjour ", preset)
    assert cache_key("Bonjour", preset) != cache_key("Salut", preset)
    assert cache_key("Bonjour", preset) != cache_key("Bonjour", VOICE_PRESETS["B"])


def test_join_clips_adds_gaps(tmp_path):
    clips = []
    for i in range(3):
        path = tmp_path / f"{i}.wav"
        _tone(500).export(path, format="wav")
        clips.append(VoiceClip(path=path, duration=0.5))
    assert len(join_clips(clips, gap_ms=200)) == pytest.approx(3 * 500 + 2 * 200, abs=5)
