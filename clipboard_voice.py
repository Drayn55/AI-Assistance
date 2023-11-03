import json
import requests
import pyperclip

import tkinter as tk
from tkinter import ttk
from threading import Thread

import keyboard
import clipboard_voice

VOICES_DATA = {}
def create_speakers_json():
    VOICEVOX_GET_SPEAKERS_URL = 'http://127.0.0.1:50021/speakers'
    r = requests.get(VOICEVOX_GET_SPEAKERS_URL)
    with open('speakers.json', 'w+', encoding='utf-8') as f:
        data = r.json()
        f.write(json.dumps(data, indent=2, ensure_ascii=False))

    return data

def get_options():
    global VOICES_DATA

    try:
        with open('speakers.json', 'r', encoding='utf-8') as f:
            VOICES_DATA = json.load(f)
    except FileNotFoundError:
        print("speakers.json not found... generating it from voicevox server.")
        VOICES_DATA = create_speakers_json()

    return  [ d['name'] for d in VOICES_DATA]


class MainVoiceWindow():
    window = None
    combo_box = None
    combo_box_2 = None
    text_widget = None
    selected_voice_id = 2
    selected_data = None
    clipboard_copy = None
    clipboard_play = None

    label_str = None

    def __init__(self, *args, **kwargs):
        clipboard_voice.japanese_text_found_callback = self.update_text_widget
        self.create_tkinter_window()

    def create_tkinter_window(self):
        # Membuat window traker
        self.window = tk.Tk()

        # Membuat daftar opsi untuk combobox
        options = get_options()

        # Membuat widget ttk Combobox dan mengatur values
        self.combo_box = ttk.Combobox(self.window, values=options, state='readonly')
        self.combo_box.set('Select an option')
        self.combo_box.bind("<<ComboboxSelected>>", self.on_voice_selected)
        self.combo_box.current(0)
        self.combo_box.pack()

        # Voice id combobox
        self.combo_box_2 = ttk.Combobox(self.window, values=[], state='readonly')
        self.combo_box_2.set('Voice style')
        self.combo_box_2.bind("<<ComboboxSelected>>", self.on_voice_style_selected)
        self.combo_box_2.pack()

        self.on_voice_selected(0)

        # check
        self.clipboard_copy = tk.BooleanVar()
        self.clipboard_copy.set(True)
        # Buat widget kotak centang dan kaitkan dengan variabel check_var dan fungsi check_callback
        check_box = tk.Checkbutton(self.window, text="Clipboard copy", variable=self.clipboard_copy, command=self.check_callback)
        check_box.pack()

        self.clipboard_play = tk.BooleanVar()
        self.clipboard_play.set(True)
        check_box = tk.Checkbutton(self.window, text="Auto play", variable=self.clipboard_play, command=self.check_callback_play)
        check_box.pack()

        # Label
        # Membuat label di atas kotak kombo dan widget teks
        self.label_str = tk.StringVar()
        self.label_str.set(f'Japanese text (voice id ={self.selected_voice_id})')
        label = tk.Label(self.window, textvariable=self.label_str)
        label.pack()

        # Membuat widget tombol
        self.button = tk.Button(self.window, text="Play voice!", command=self.create_voice_from_text)
        self.button.pack(side=tk.RIGHT)

        # Text
        # Membuat widget teks untuk menampilkan opsi yang dipilih
        self.window.after(1000, self.check_clipboard_change)
        self.text_widget = tk.Text(self.window, height=2, state='normal')
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        


        self.thread = Thread(target=clipboard_voice.run_clipboard_voice)
        self.thread.start()

        # Shortcuts

        keyboard.add_hotkey('win+z', self.create_voice_from_text)
        keyboard.add_hotkey('win+c', self.switch_auto_play)


        # Memulai perulangan kegiatan tkinter
        self.window.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.window.mainloop()

    def on_exit(self):
        clipboard_voice.EXIT_PROGRAM = True

        self.window.destroy()
        print('Exiting...')

    def check_callback(self):
        clipboard_voice.CHECK_CLIPBOARD = self.clipboard_copy.get()
        print("Check box clip:", self.clipboard_copy.get())

    def check_callback_play(self):
        clipboard_voice.CLIPBOARD_AUTO_PLAY = self.clipboard_play.get()
        print("Check box play:", self.clipboard_play.get())

    def switch_auto_play(self):
        self.clipboard_play.set(not self.clipboard_play.get())
        self.check_callback_play()

    def create_voice_from_text(self):
        sentence = self.text_widget.get('1.0', tk.END).strip()##########
        print('Sending: ' + sentence)
        #clipboard_voice.check_new_text_and_play_voice(True, sentence)
        clipboard_voice.speak_jp(sentence, play_new_voice=True)

    def run_voice_on_change(self):
        sentence = self.text_widget.get('1.0', tk.END)
        self.create_voice_from_text()

    def check_clipboard_change(self):
        clipboard_text = pyperclip.paste()
        if clipboard_text != self.text_widget.get("1.0", tk.END).strip():
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, clipboard_text)
            self.text_updated = True  # Tandai bahwa teks telah diubah
        else:
            if self.text_updated:
                # Jika teks telah diubah, atur ulang timer
                self.text_updated = False  # Reset tandai
                self.window.after(1000, self.check_clipboard_change)
            else:
                # Jika teks tidak berubah, hapus secara otomatis setelah 1 detik
                self.text_widget.delete("1.0", tk.END)

        # Tetap panggil fungsi check_clipboard_change setiap 1 detik
        self.window.after(1000, self.check_clipboard_change)###########

    def on_voice_selected(self, event):
        selected_option = self.combo_box.get()
        selected_index = self.combo_box.current()
        print('Selected option:', selected_option)
        print('Selected index:', selected_index)

        self.setup_voice_styles_combobox(selected_index)

    def on_voice_style_selected(self, event):
        selected_option = self.combo_box_2.get()
        selected_index = self.combo_box_2.current()
        print('Selected option:', selected_option)
        print('Selected combobox index:', selected_index)

        self.update_voice_id_selected()

    def setup_voice_styles_combobox(self, id):
        self.selected_data = VOICES_DATA[id]['styles']
        options = [d['name'] for d in VOICES_DATA[id]['styles']]
        print(options)
        self.combo_box_2.option_clear()
        self.combo_box_2['values'] = options
        self.combo_box_2.current(0)

        self.selected_voice_id = self.selected_data[0]['id']
        clipboard_voice.VOICE_ID = int(self.selected_voice_id)
        print('Selected id: ' + str(self.selected_voice_id))

    def update_voice_id_selected(self):
        selected_id = self.combo_box_2.current()
        self.selected_voice_id = self.selected_data[selected_id]['id']

        selected_style = str(self.selected_data[selected_id]['name'])
        print('Selected style:' + selected_style)
        print('Selected voice_id: ' + str(self.selected_voice_id))

        self.label_str.set(f'Japanese text (voice id ={self.selected_voice_id})')
        clipboard_voice.VOICE_ID = int(self.selected_voice_id)

    def update_text_widget(self, text):
        print('Updated text widget')
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert(tk.END, text.strip())



if __name__ == '__main__':
    print("Starting...")
    print("win+z to play voice. (button hotkey)")
    print("win+c to switch auto-play checkbox")
    MainVoiceWindow()