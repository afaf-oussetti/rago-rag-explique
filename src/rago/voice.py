"""Voix de Rago : texte vers audio robot (edge-tts + effet pydub) et durée de chaque réplique.

Chaque réplique passe par trois étapes :

1. edge-tts lit le texte avec une voix française (connexion internet nécessaire) ;
2. pydub ajoute l'effet robot : une touche métallique et un écho très court ;
3. le résultat est mis en cache dans ``cache/voice/`` : une réplique déjà générée
   n'est jamais redemandée.
"""

from __future__ import annotations

import asyncio
import hashlib
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import edge_tts
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import detect_leading_silence

DEFAULT_CACHE_DIR = Path("cache") / "voice"


@dataclass(frozen=True)
class VoicePreset:
    """Réglages d'une voix robot.

    Attributes:
        name: Nom lisible du préréglage.
        voice: Voix edge-tts, par exemple ``fr-FR-HenriNeural``.
        rate: Vitesse de lecture edge-tts (``"+5%"``, ``"-10%"``...).
        pitch: Hauteur de voix edge-tts, en hertz (``"+20Hz"``...).
        metal_mix: Dose de son métallique, de 0 (aucun) à 1 (robot pur).
        metal_freq: Fréquence de la modulation métallique, en hertz.
        echo_delay_ms: Retard de l'écho en millisecondes (0 = pas d'écho).
        echo_gain_db: Volume de l'écho par rapport à la voix, en décibels.
    """

    name: str
    voice: str
    rate: str = "+0%"
    pitch: str = "+0Hz"
    metal_mix: float = 0.0
    metal_freq: float = 60.0
    echo_delay_ms: int = 0
    echo_gain_db: float = -16.0


VOICE_PRESETS: dict[str, VoicePreset] = {
    "A": VoicePreset(
        name="Petit robot malin",
        voice="fr-FR-HenriNeural",
        rate="+5%",
        pitch="+25Hz",
        echo_delay_ms=45,
    ),
    "B": VoicePreset(
        name="Robot mignon",
        voice="fr-FR-EloiseNeural",
        pitch="+10Hz",
        metal_mix=0.15,
        metal_freq=70.0,
        echo_delay_ms=40,
    ),
    "C": VoicePreset(
        name="Robot classique doux",
        voice="fr-FR-RemyMultilingualNeural",
        pitch="+15Hz",
        metal_mix=0.3,
        metal_freq=55.0,
        echo_delay_ms=55,
        echo_gain_db=-14.0,
    ),
}


# La voix officielle de Rago dans la série (choisie au jalon 2).
RAGO_VOICE = VOICE_PRESETS["A"]


@dataclass(frozen=True)
class VoiceClip:
    """Une réplique générée : son fichier audio et sa durée en secondes."""

    path: Path
    duration: float


# --- Effets audio (sans réseau, testables) -----------------------------------------


def _to_array(audio: AudioSegment) -> np.ndarray:
    return np.array(audio.get_array_of_samples(), dtype=np.float64)


def _from_array(samples: np.ndarray, like: AudioSegment) -> AudioSegment:
    limit = float(2 ** (8 * like.sample_width - 1) - 1)
    clipped = np.clip(samples, -limit, limit).astype(
        np.int16 if like.sample_width == 2 else np.int32
    )
    return like._spawn(clipped.tobytes())


def add_metal(audio: AudioSegment, mix: float, freq: float) -> AudioSegment:
    """Ajoute une touche métallique (modulation en anneau dosée), sans changer la durée.

    Args:
        audio: Son mono d'origine.
        mix: Dose d'effet, de 0 (aucun) à 1 (effet complet).
        freq: Fréquence de modulation en hertz : plus elle est haute, plus le son est métallique.
    """
    if mix <= 0:
        return audio
    samples = _to_array(audio)
    t = np.arange(len(samples)) / audio.frame_rate
    modulated = samples * np.sin(2 * np.pi * freq * t)
    return _from_array((1 - mix) * samples + mix * modulated, audio)


def add_echo(audio: AudioSegment, delay_ms: int, gain_db: float) -> AudioSegment:
    """Ajoute un écho très court, sans changer la durée.

    Args:
        audio: Son d'origine.
        delay_ms: Retard de l'écho en millisecondes (0 = pas d'écho).
        gain_db: Volume de l'écho par rapport à l'original, en décibels (négatif = plus bas).
    """
    if delay_ms <= 0:
        return audio
    return audio.overlay(audio + gain_db, position=delay_ms)


def trim_silence(
    audio: AudioSegment, threshold_db: float = -45.0, keep_ms: int = 60
) -> AudioSegment:
    """Retire les silences au début et à la fin, en gardant une petite marge.

    Args:
        audio: Son d'origine.
        threshold_db: En dessous de ce volume (dBFS), le son est considéré comme silence.
        keep_ms: Marge de silence conservée de chaque côté, en millisecondes.
    """
    start = detect_leading_silence(audio, silence_threshold=threshold_db)
    end = detect_leading_silence(audio.reverse(), silence_threshold=threshold_db)
    start = max(0, start - keep_ms)
    stop = min(len(audio), len(audio) - end + keep_ms)
    return audio[start:stop] if stop > start else audio


def apply_robot_effect(audio: AudioSegment, preset: VoicePreset) -> AudioSegment:
    """Transforme une voix naturelle en voix de Rago, selon le préréglage."""
    audio = trim_silence(audio.set_channels(1))
    audio = add_metal(audio, preset.metal_mix, preset.metal_freq)
    audio = add_echo(audio, preset.echo_delay_ms, preset.echo_gain_db)
    return normalize(audio, headroom=1.0)


# --- Génération ----------------------------------------------------------------------


def cache_key(text: str, preset: VoicePreset) -> str:
    """Calcule l'identifiant de cache d'une réplique (il change avec le texte ou un réglage)."""
    payload = repr((text.strip(), sorted(asdict(preset).items())))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def duration_seconds(path: Path) -> float:
    """Renvoie la durée d'un fichier audio, en secondes."""
    return len(AudioSegment.from_file(path)) / 1000


def _speak(text: str, preset: VoicePreset, output_path: Path) -> None:
    """Fait lire le texte par edge-tts et enregistre le MP3 brut (connexion internet requise)."""
    communicate = edge_tts.Communicate(text, preset.voice, rate=preset.rate, pitch=preset.pitch)
    asyncio.run(communicate.save(str(output_path)))


def generate_line(text: str, preset: VoicePreset, cache_dir: Path = DEFAULT_CACHE_DIR) -> VoiceClip:
    """Génère (ou récupère dans le cache) l'audio robot d'une réplique.

    Args:
        text: La réplique à dire.
        preset: Le préréglage de voix.
        cache_dir: Dossier du cache audio.

    Returns:
        Le fichier WAV de la réplique et sa durée en secondes.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_path = cache_dir / f"{cache_key(text, preset)}.wav"

    if not output_path.exists():
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = Path(tmp) / "brut.mp3"
            _speak(text, preset, raw_path)
            raw = AudioSegment.from_file(raw_path)
        apply_robot_effect(raw, preset).export(output_path, format="wav")

    return VoiceClip(path=output_path, duration=duration_seconds(output_path))


def join_clips(clips: list[VoiceClip], gap_ms: int = 400) -> AudioSegment:
    """Met plusieurs répliques bout à bout, séparées par un court silence."""
    result = AudioSegment.empty()
    for index, clip in enumerate(clips):
        if index:
            result += AudioSegment.silent(duration=gap_ms)
        result += AudioSegment.from_file(clip.path)
    return result
