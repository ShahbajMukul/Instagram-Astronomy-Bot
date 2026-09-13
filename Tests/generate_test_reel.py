"""Generate a short Instagram-compatible reel without using Cartesia."""

import os

import numpy
from moviepy import AudioClip, ColorClip


def generate_test_reel(output_path=None):
    output_path = output_path or os.path.join(
        os.path.dirname(__file__), "test_reel.mp4"
    )
    duration = 5

    def make_audio(t):
        frequency = 440
        samples = numpy.asarray(t)
        values = 0.15 * numpy.sin(2 * numpy.pi * frequency * samples)
        return values if samples.ndim else float(values)

    video = ColorClip(size=(1080, 1920), color=(12, 28, 52), duration=duration)
    audio = AudioClip(make_audio, duration=duration, fps=44100)
    video = video.with_audio(audio)
    video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=30,
        audio_fps=44100,
        bitrate="2500k",
        ffmpeg_params=[
            "-pix_fmt", "yuv420p",
            "-profile:v", "main",
            "-level", "4.2",
            "-movflags", "+faststart",
        ],
        logger=None,
    )
    video.close()
    audio.close()
    return output_path


if __name__ == "__main__":
    path = generate_test_reel()
    print(path)