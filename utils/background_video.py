import time

from moviepy.editor import *
import moviepy.editor as mp
from PIL import Image


from utils.Server import get_config, download_file, get_path
from utils.settings import get_settings


LOGOTYPES_PATH = get_config()['LOGOTYPES_PATH']
OUTPUT_PATH = get_config()["OUTPUT_PATH"]


def divide_number_by_max_min_parts(number, min_part, max_part):
    num_parts = number / max_part
    whole_num_parts = int(num_parts)

    # If the number is exactly divisible by max_part
    if num_parts == whole_num_parts:
        return [max_part] * whole_num_parts

    # If the number is not exactly divisible
    fractional_part = number / (whole_num_parts + 1)

    # Check if the fractional part is less than the min_part
    if fractional_part < min_part:
        return [number]

    parts = [fractional_part] * (whole_num_parts + 1)

    return parts


def get_durations(subtitles, message_id):
    subtitles = [i for i in subtitles if i[1] != '']

    clips_settings = get_settings(message_id)['clips_settings']
    video_settings = get_settings(message_id)['video_settings']

    durations = [0]

    duration = 0

    for index, word in enumerate(subtitles):
        if index == len(subtitles)-1 or subtitles[index+1][0] != subtitles[index][1]:
            if duration >= clips_settings['max_duration']:
                pass
            duration = word[0][1] - sum(durations)

        if clips_settings['min_duration'] <= duration <= clips_settings['max_duration']:
            durations.append(duration)

        elif index == len(subtitles)-1 and duration <= clips_settings['max_duration']:
            durations.append(duration)

        else:
            durations += divide_number_by_max_min_parts(duration,
                                                        clips_settings['min_duration'], clips_settings['max_duration'])

    durations += divide_number_by_max_min_parts(video_settings['after_phrase_duration'],
                                                clips_settings['min_duration'], clips_settings['max_duration'])

    if sum(durations) < video_settings['min_duration']:
        durations += divide_number_by_max_min_parts(video_settings['min_duration'] - sum(durations),
                                                    clips_settings['min_duration'], clips_settings['max_duration'])

    return durations[1:]


def create_background_video(durations, clips_path):
    t1 = time.time()
    clips_path = get_config()['VIDEOS_PATH'] + "\\" + clips_path
    final_clips = []

    clips = []
    for duration in durations:
        while True:
            clip_path = get_path(clips_path, clips)

            if '.mp4' not in clip_path and '.m4a' not in clip_path and '.mov' not in clip_path:
                continue

            clips.append(clip_path)

            download_file(clip_path)
            time.sleep(0.5)

            clip = VideoFileClip(clip_path).without_audio()
            if clip.duration >= duration:
                final_clips.append(clip.subclip(0, duration).resize((1080, 1920)))
                break

            clip.close()

    # join all clips in one video
    video = concatenate_videoclips(final_clips)

    return video


def add_logo(video, message_id, user_id):
    path = f'{LOGOTYPES_PATH}\\{user_id}.png'

    video_settings = get_settings(message_id)['video_settings']

    if download_file(path) == 200:
        image = Image.open(path)

        w, h = image.size

        p = 250 / w

        image.close()

        logo = (mp.ImageClip(path)
                .set_duration(video.duration)
                .resize(p)
                .margin(right=0, top=0, bottom=video_settings['logo_position'], opacity=0)
                .set_pos(("center", "bottom")))

        video = mp.CompositeVideoClip([video, logo], use_bgclip=True)

    return video


if __name__ == '__main__':
    subtitles = [[[0.0, 0.64], 'Your time is'],
                 [[0.64, 0.92], 'limited,'],
                 [[0.92, 0.96], ''],
                 [[0.96, 1.58], "so don't waste"],
                 [[1.58, 2.32], 'it living someone'],
                 [[2.32, 2.96], "else's life."]]

    from pprint import pprint
    pprint(get_durations(subtitles, 'config'))
