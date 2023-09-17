from utils.background_video import create_background_video, add_logo, get_durations
from utils.audio import add_combined_audio
from utils.subtitles import add_video_subtitles, get_subtitles
from utils.settings import get_settings
from utils.Server import get_config
from utils.voice import generate_voice, get_words

from moviepy.editor import *


OUTPUT_PATH = get_config()["OUTPUT_PATH"]
VOICE_PATH = get_config()["VOICE_PATH"]


def generate_video(message_id, user_id):
    settings = get_settings(message_id)

    generate_voice(settings['text'], message_id)

    if settings["subtitles_settings"]['visibility']:
        words = get_words(message_id)
        subtitles = get_subtitles(words)
    else:
        start = 0
        end = AudioFileClip(f'{VOICE_PATH}\\{message_id}.wav').duration
        text = ''

        subtitles = [[[start, end], text]]

    durations = get_durations(subtitles, message_id)
    duration = sum(durations)

    video = create_background_video(durations, settings['clips_settings']['clips_path'])

    video = add_logo(video, message_id, user_id)

    if settings["subtitles_settings"]['visibility']:
        video = add_video_subtitles(video, subtitles, message_id)

    video = add_combined_audio(video, message_id, duration)

    video.write_videofile(f"{OUTPUT_PATH}\\{message_id}.mp4",
                          audio_codec='aac',
                          threads=16,
                          fps=30,
                          codec='libx264')


if __name__ == '__main__':
    import time

    t1 = time.time()
    generate_video('config', '1196962259')
    print(time.time() - t1)