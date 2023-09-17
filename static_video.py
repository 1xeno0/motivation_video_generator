from utils.background_video import create_background_video, add_logo, get_durations
from utils.audio import add_background_audio
from utils.subtitles import add_video_subtitles
from utils.settings import get_settings
from utils.Server import get_config


OUTPUT_PATH = get_config()["OUTPUT_PATH"]


def generate_video(message_id, user_id):
    settings = get_settings(message_id)

    start = 0
    duration = end = settings['video_settings']['min_duration']
    text = settings['text']

    subtitles = [[[start, end], text]]

    durations = get_durations(subtitles, message_id)

    video = create_background_video(durations, settings['clips_settings']['clips_path'])

    video = add_logo(video, message_id, user_id)

    if settings["subtitles_settings"]['visibility']:
        video = add_video_subtitles(video, subtitles, message_id)

    video = add_background_audio(video, message_id, duration)

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