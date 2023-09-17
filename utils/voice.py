import requests
import json
import os

from langdetect import detect
import whisper

from utils.Server import get_config


config = get_config()

ELEVENLABS_API = config["ELEVENLABS_API"]
VOICE_PATH = config["VOICE_PATH"]


def generate_voice(text, id):
    if detect(text) != 'en':
        model_id = "eleven_multilingual_v1"
    else:
        model_id = "eleven_monolingual_v1"

    api_key = ELEVENLABS_API

    voice_id = 'pNInz6obpgDQGcFmaJgB'
    href = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'

    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": model_id
    }

    audio = requests.post(href, data=json.dumps(payload), headers=headers)
    with open(f'{VOICE_PATH}/{id}.wav', 'wb+') as f:
        f.write(audio.content)


def get_words(id):
    model = whisper.load_model("medium")
    result = model.transcribe(f'{VOICE_PATH}/{id}.wav', word_timestamps=True)

    pre_words = []
    for segment in result['segments']:
        pre_words += [{'word': word['word'].strip(), 'start': word['start'], 'end': word['end']} for word in segment['words']]

    return pre_words


if __name__ == '__main__':
    generate_voice("Your time is limited, so don't waste it living someone else's life", '1')

    words = get_words('1')
    from pprint import pprint
    pprint(words)
