"""Assemblage final : animation + voix + sous-titres + signature, puis export MP4."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np

from rago import theme
from rago.subtitles import SubtitleChunk, render_chunk, render_signature, y_to_pixels
from rago.timing import Timeline
from rago.voice import VoiceClip


def assemble(
    video_path: Path,
    clips: Sequence[VoiceClip],
    timeline: Timeline,
    subtitles: Sequence[SubtitleChunk],
    output_path: Path,
) -> Path:
    """Monte la vidéo finale avec MoviePy.

    Args:
        video_path: L'animation Manim, sans le son.
        clips: L'audio de chaque réplique, dans l'ordre.
        timeline: Le minutage (moment où commence chaque réplique).
        subtitles: Les sous-titres et leurs horaires.
        output_path: Le fichier MP4 à créer.

    Returns:
        Le chemin de la vidéo finale.
    """
    from moviepy import (
        AudioFileClip,
        CompositeAudioClip,
        CompositeVideoClip,
        ImageClip,
        VideoFileClip,
    )

    video = VideoFileClip(str(video_path))
    voice = CompositeAudioClip(
        [
            AudioFileClip(str(clip.path)).with_start(cue.start)
            for clip, cue in zip(clips, timeline.cues, strict=True)
        ]
    ).with_duration(video.duration)

    layers = [video]
    for chunk in subtitles:
        image = np.array(render_chunk(chunk))
        top = y_to_pixels(theme.SUBTITLE_Y) - image.shape[0] / 2
        layers.append(
            ImageClip(image)
            .with_start(chunk.start)
            .with_end(min(chunk.end, video.duration))
            .with_position(("center", top))
        )

    signature = np.array(render_signature())
    top = y_to_pixels(theme.SIGNATURE_Y) - signature.shape[0] / 2
    layers.append(ImageClip(signature).with_duration(video.duration).with_position(("center", top)))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final = CompositeVideoClip(layers, size=(theme.VIDEO_WIDTH, theme.VIDEO_HEIGHT)).with_audio(
        voice
    )
    final.write_videofile(
        str(output_path),
        fps=theme.FPS,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k",
        logger=None,
    )
    video.close()
    return output_path
