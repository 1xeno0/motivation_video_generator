import time

from utils.settings import get_settings
from utils.Server import get_config, download_file, get_path

from moviepy.editor import *
from moviepy.audio.fx.all import volumex


config = get_config()

MUSIC_PATH = config["MUSIC_PATH"]
VOICE_PATH = config["VOICE_PATH"]
OUTPUT_PATH = get_config()["OUTPUT_PATH"]


def get_voice_audio(message_id):
    audio_settings = get_settings(message_id)["audio_settings"]

    voice_clip = AudioFileClip(f'{VOICE_PATH}\\{message_id}.wav')

    voice_clip = voice_clip.fx(volumex, audio_settings['voice_volume'])

    return voice_clip


def get_background_audio(message_id, duration):
    audio_settings = get_settings(message_id)["audio_settings"]

    music_list = []

    while True:
        music_path = get_path(f'{MUSIC_PATH}', music_list)
        if '.mp3' not in music_path and '.wav' in music_path:
            continue

        music_list.append(music_path)

        download_file(music_path)

        time.sleep(0.5)

        audio_clip = AudioFileClip(music_path)

        if audio_clip.duration >= duration:
            audio_clip = audio_clip.subclip(0, duration)
            audio_clip = audio_clip.fx(volumex, audio_settings['background_audio_volume'])

            return audio_clip


def add_background_audio(video, message_id, duration):
    music_clip = get_background_audio(message_id, duration)

    video.audio = music_clip

    return video


def add_audio(video, message_id):
    voice_clip = get_voice_audio(message_id)

    video.audio = voice_clip

    return video


def add_combined_audio(video, message_id, duration):
    voice_clip = get_voice_audio(message_id)
    music_clip = get_background_audio(message_id, duration)

    final_audio_clip = CompositeAudioClip([music_clip, voice_clip])

    video.audio = final_audio_clip

    return video
