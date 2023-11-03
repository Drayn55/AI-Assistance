import openai
import sys
import pytchat
import time
import pyaudio
import keyboard
import wave
import threading
import googletrans
import pyperclip
import socket
import clipboard_voice
from gtts import gTTS 
from config import *
from utils.translate import *
from utils.TTS import *
from utils.subtitle import *
from utils.promptMaker import *
from utils.twitch_config import *



sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)


openai.api_key = api_key

conversation = []

history = {"history": conversation}

mode = 0
total_characters = 0
chat = ""
chat_now = ""
chat_prev = ""
is_Speaking = False
owner_name = "Drayn"
blacklist = ["Nightbot", "streamelements"]


def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "input.wav"
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    print("Recording...")
    while keyboard.is_pressed('RIGHT_SHIFT'):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Stopped recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    transcribe_audio("input.wav")


def transcribe_audio(file):
    global chat_now
    try:
        audio_file= open(file, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        chat_now = transcript.text
        print ("Question: " + chat_now)
    except:
        print("Error transcribing audio: {0}".format(e))
        return

    result = owner_name + " said " + chat_now
    conversation.append({'role': 'user', 'content': result})
    openai_answer()


def openai_answer():
    global total_characters, conversation

    total_characters = sum(len(d['content']) for d in conversation)

    while total_characters > 4000:
        try:
            conversation.pop(2)
            total_characters = sum(len(d['content']) for d in conversation)
        except Exception as e:
            print("Error removing old messages: {0}".format(e))

    with open("conversation.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    prompt = getPrompt()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        max_tokens=128,
        temperature=0.6,
        top_p=0.9
    )
    
    conversation.append({'role': 'assistant', 'content': response['choices'][0]['message']['content']})

    message = response['choices'][0]['message']['content']
    translate_text(message)

    
def to_str(obj):
    try:
        return str(obj)
    except Exception:
        return ""
    
def translate_text(text):
    global is_Speaking


    detect = detect_google(text)

    tts = translate_google(text, f"{detect}", "JA")
    tts_en = translate_google(text, f"{detect}", "EN")
    tts_id = translate_google(text, f"{detect}", "ID")
    try:

        print("JP Response: " + to_str(tts))
        print("EN Response: " + tts_en)
        print("ID Response: " + tts_id)

    except Exception as e:
        print("Error printing text: {0}".format(e))
        return

    pyperclip.copy(to_str(tts))
    

def clear_text_files():
    with open("output.txt", "w") as f:
        f.truncate(0)
    with open("chat.txt", "w") as f:
        f.truncate(0)


def preparation():
    global conversation, chat_now, chat, chat_prev
    while True:
       
        chat_now = chat
        if is_Speaking == False and chat_now != chat_prev:
            conversation.append({'role': 'user', 'content': chat_now})
            chat_prev = chat_now
            openai_answer()
        time.sleep(1)

if __name__ == "__main__":
    try:
      
        mode = input("Mode (1-Microphone, 2-Typing, ): ")

        if mode == "1":
            print("Press and Hold Right Shift to record audio")
            while True:
                if keyboard.is_pressed('RIGHT_SHIFT'):
                    record_audio()
        

        elif mode == "2":
            while True:
                user_input = input("Question: ")
                conversation.append({'role': 'user', 'content': user_input})
                openai_answer()
                clear_text_files()

        print("Stopped")


    except KeyboardInterrupt:
        t.join()
        print("Stopped")

