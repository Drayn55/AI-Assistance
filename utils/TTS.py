import os
import torch
import requests
import urllib.parse
from utils.katakana import *

def voicevox_tts(tts):


    voicevox_url = 'http://localhost:50021'
    katakana_text = katakana_converter(tts)
    params_encoded = urllib.parse.urlencode({'text': katakana_text, 'speaker': 46})
    request = requests.post(f'http://127.0.0.1:50021/audio_query?{params_encoded}')
    params_encoded = urllib.parse.urlencode({'speaker': 46, 'enable_interrogative_upspeak': True})
    request = requests.post(f'http://127.0.0.1:50021/synthesis?{params_encoded}', json=request.json())

    with open("test.wav", "wb") as outfile:
        outfile.write(request.content)

if __name__ == "__main__":
    silero_tts()
