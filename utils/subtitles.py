import time

import cv2
from moviepy.editor import *
import moviepy.editor as mp
from PIL import Image, ImageDraw, ImageFont
import re
import numpy as np

from utils.settings import get_settings
from utils.Server import get_config, download_file


config = get_config()
OUTPUT_PATH = get_config()["OUTPUT_PATH"]


def find_emoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)

    return bool(emoji_pattern.search(text))


def filter_text(text):
    badWords = {
        'fuck': 'f*ck',
        'shit': 'sh*t',
        'bitch': 'b*tch',
        'motherfucker': 'm*therfucker',
        'Fuck': 'F*ck',
        'Shit': 'Sh*t',
        'Ass': '*ss',
        'Bitch': 'B*tch',
        'Motherfucker': 'M*therfucker'
    }

    for i in badWords:
        text = text.replace(i, badWords[i])

    return text


def get_subtitles(words):

    subtitles = []

    subtitle = []
    for index, word in enumerate(words):
        subtitle.append(word)

        if index == len(words)-1 or len(subtitle) == 3 or words[index+1]['start'] != words[index]['end']:
            text = ' '.join([i['word'] for i in subtitle])
            start = subtitle[0]['start']
            end = subtitle[-1]['end']

            if subtitles and subtitles[-1][0][1] != start:
                subtitles.append([[subtitles[-1][0][1], start], ''])

            subtitles.append([[start, end], text])
            subtitle = []

    return subtitles


def add_static_text(frame, text, message_id):
    subtitles_settings = get_settings(message_id)["subtitles_settings"]

    text = filter_text(text) + '\n'

    # Convert the OpenCV frame to a PIL image
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)

    download_file(f'{config["FONTS_PATH"]}/' + subtitles_settings["font_path"])
    time.sleep(0.5)

    font = ImageFont.truetype(font=f'{config["FONTS_PATH"]}/' + subtitles_settings["font_path"],
                              size=subtitles_settings["font_size"])

    all_text = []
    for x in text.split('\n'):
        saveText = ''
        index = 0
        for i in x.split():
            width_text, h = draw.textsize(saveText.split('\n')[index], font=font)
            if width_text / 1080 > subtitles_settings["maxTextWidth"]:
                saveText += f'\n{i}'
                index += 1
            else:
                saveText += f' {i}'
        all_text += saveText.split('\n')


    if len(all_text) > 1:
        text = '\n'.join(all_text)

    maxTextH = max(draw.textsize(i, font=font)[1] for i in text.split('\n'))

    distance = 0

    height_text = 960 - (maxTextH + distance) * len(text.split('\n')) // 2
    for index, i in enumerate(text.split('\n')):
        width_text, h = draw.textsize(i, font=font)
        org_x, org_y = (540 - width_text // 2, height_text + index * (maxTextH + distance))

        draw.text((org_x, org_y), i.strip(), font=font, fill=tuple(subtitles_settings["font_color"]),
                  stroke_width=subtitles_settings["stroke_width"], stroke_fill=(0, 0, 0))

    frame_with_text = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

    return frame_with_text


def add_video_subtitles(video, subtitles, message_id):
    clips = []

    for index, i in enumerate(subtitles):
        if i[1] != '':
            clip = video.subclip(i[0][0], i[0][1])

            if find_emoji(i[1]):
                emoji = create_emoji(message_id, i[1])
            else:
                emoji = create_text(message_id, i[1])

            clip_with_text = add_text(clip, emoji)

            clips.append(clip_with_text)
        else:
            clip = video.subclip(i[0][0], i[0][1])
            clips.append(clip)

    video = mp.concatenate_videoclips(clips)

    return video


def add_text(clip, emoji):

    w, h, path = emoji

    text = (mp.ImageClip(path)
            .set_duration(clip.duration)
            .set_position("center", "center"))

    clip = mp.CompositeVideoClip([clip, text], use_bgclip=True)

    return clip


def create_text(message_id, text):
    settings = get_settings(message_id)
    subtitles_settings = settings["subtitles_settings"]

    text = filter_text(text)

    # Load the font
    font_path = f'{config["FONTS_PATH"]}\\{settings["subtitles_settings"]["font_path"]}'
    download_file(font_path)
    time.sleep(0.5)

    font = ImageFont.truetype(font_path, subtitles_settings['font_size'])

    # Create a transparent image
    text_width, text_height = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textsize(text, font=font)
    image = Image.new('RGBA', (text_width, text_height))

    # Draw the text onto the image
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text.strip(), font=font, fill=tuple(subtitles_settings["font_color"]),
              stroke_width=subtitles_settings["stroke_width"], stroke_fill=(0, 0, 0))

    # Save the image as PNG
    output_path = f"{config['EMOJIS_PATH']}/{message_id}.png"
    image.save(output_path, "PNG")
    image.close()

    return 540 - int(text_width / 137 * settings['subtitles_settings']['font_size']) // 2, 960, output_path


def create_emoji(message_id, text):
    settings = get_settings(message_id)

    # Load the font
    font_path = f'{config["FONTS_PATH"]}\\{"appleMain.ttf"}'
    download_file(font_path)
    time.sleep(0.5)

    font = ImageFont.truetype(font_path, 137)

    # Create a transparent image
    text_width, text_height = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textsize(text, font=font)
    image = Image.new('RGBA', (text_width, text_height))

    # Draw the text onto the image
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, embedded_color=True)

    image = image.resize((int(text_width / 137 * settings['subtitles_settings']['font_size']),
                          int(text_height / 137 * settings['subtitles_settings']['font_size'])))

    # Save the image as PNG
    output_path = f"{config['EMOJIS_PATH']}/{message_id}.png"
    image.save(output_path, "PNG")
    image.close()

    return 540 - int(text_width / 137 * settings['subtitles_settings']['font_size']) // 2, 960, output_path


if __name__ == '__main__':
    words = [{'end': 0.26, 'start': 0.0, 'word': 'Your'},
             {'end': 0.46, 'start': 0.26, 'word': 'time'},
             {'end': 0.64, 'start': 0.46, 'word': 'is'},
             {'end': 0.92, 'start': 0.64, 'word': 'limited,'},
             {'end': 1.14, 'start': 0.96, 'word': 'so'},
             {'end': 1.34, 'start': 1.14, 'word': "don't"},
             {'end': 1.58, 'start': 1.34, 'word': 'waste'},
             {'end': 1.8, 'start': 1.58, 'word': 'it'},
             {'end': 2.0, 'start': 1.8, 'word': 'living'},
             {'end': 2.32, 'start': 2.0, 'word': 'someone'},
             {'end': 2.84, 'start': 2.32, 'word': "else's"},
             {'end': 2.96, 'start': 2.84, 'word': 'life.'}]

    from pprint import pprint

    pprint(get_subtitles(words))
