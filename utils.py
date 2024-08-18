import random
from tkinter import Label, Entry, StringVar, END, Button
from tkinter import filedialog
from gtts import gTTS
from pygame import mixer
from deep_translator import GoogleTranslator
import tempfile
import os
from PyPDF2 import PdfReader
import re
import string

# PDF işleme fonksiyonu
def process_pdf(file_path):
    stop_words = [
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
        "you're", "you've", "you'll", "you'd", 'your', 'yours',
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself',
        'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a',
        'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
        'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
        'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
        'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't",
        'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
        'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't",
        'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
    ]
    stop_words.extend(list(string.punctuation))
    stop_words.extend(list(string.ascii_lowercase))
    stop_words.extend(list(string.ascii_uppercase))
    stop_words.extend([str(i) for i in range(10)])

    pdf_reader = PdfReader(file_path)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    words = text.lower().split()
    filtered_words = [re.sub(r'[^\w\s]', '', word) for word in words if word not in stop_words and re.sub(r'[\d]', '', word) and len(re.sub(r'[^\w\s]', '', word)) > 2]
    
    return filtered_words

class TypingPracticeApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Typing Practice with Pronunciation")
        self.master.configure(bg='black')
        
        self.center_window(600, 250)

        # Initialize StringVars
        self.current_word = StringVar()
        self.translated_word = StringVar()
        
        # Word list and used words
        self.word_list = []
        self.used_words = []

        # UI components
        self.create_widgets()
        
        # Initialize the mixer
        mixer.init()

    def center_window(self, width=600, height=250):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        center_x = int(screen_width / 2 - width / 2)
        center_y = int(screen_height / 2 - height / 2)
        self.master.geometry(f'{width}x{height}+{center_x}+{center_y}')

    def create_widgets(self):
        self.word_label = Label(self.master, textvariable=self.current_word, font=('Helvetica', 24), fg='white', bg='black')
        self.word_label.pack()

        self.translation_label = Label(self.master, textvariable=self.translated_word, font=('Helvetica', 18), fg='grey', bg='black')
        self.translation_label.pack()

        self.total_words_label = Label(self.master, text=f"Total Words: {len(self.word_list)}", font=('Helvetica', 12), fg='white', bg='black')
        self.total_words_label.pack()

        self.typed_words_label = Label(self.master, text="Words Typed: 0", font=('Helvetica', 12), fg='white', bg='black')
        self.typed_words_label.pack()

        self.text_entry = Entry(self.master, font=('Helvetica', 24), fg='white', bg='black', insertbackground='white')
        self.text_entry.pack()
        self.text_entry.bind('<KeyRelease>', self.on_key_release)
        self.text_entry.bind('<Tab>', self.on_tab_press)
        self.text_entry.focus()

        # PDF yükleme butonu
        self.upload_button = Button(self.master, text="Upload PDF", command=self.upload_pdf, font=('Helvetica', 12), fg='black', bg='white')
        self.upload_button.pack()

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.word_list = process_pdf(file_path)
            self.used_words = []
            self.total_words_label.config(text=f"Total Words: {len(self.word_list)}")
            self.next_word()

    def on_tab_press(self, event):
        self.pronounce(self.current_word.get())
        self.next_word()
        self.update_typed_words_count()
        return 'break'  # Prevent default Tab behavior
    
    def update_typed_words_count(self):
        self.typed_words_label.config(text=f"Words Typed: {len(self.used_words)}")

    def on_key_release(self, event):
        typed_text = self.text_entry.get().strip().lower()
        correct_word = self.current_word.get().lower()
        
        if typed_text:
            self.word_label.config(fg='green' if correct_word.startswith(typed_text) else 'red')
        
        if typed_text == correct_word:
            self.pronounce(correct_word)
            self.next_word()
            self.update_typed_words_count()

    def next_word(self):
        if len(self.used_words) == len(self.word_list):
            self.used_words.clear()
            self.update_typed_words_count()
        
        available_words = [word for word in self.word_list if word not in self.used_words]
        if not available_words:
            print("All words have been used. Resetting the list.")
            return

        new_word = random.choice(available_words)
        self.used_words.append(new_word)
        self.current_word.set(new_word)
        self.translate(new_word)
        self.text_entry.delete(0, END)

    def translate(self, word):
        try:
            translation = GoogleTranslator(source='en', target='tr').translate(word)
            self.translated_word.set(translation)
        except Exception as e:
            self.translated_word.set("Translation Error!")
            print(f"Translation error: {e}")

    def pronounce(self, word):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as fp:
                tts = gTTS(text=word, lang='en')
                tts_file = f'{fp.name}.mp3'
                tts.save(tts_file)
                mixer.music.load(tts_file)
                mixer.music.play()
                while mixer.music.get_busy():
                    continue
                os.unlink(tts_file)
        except Exception as e:
            print("Pronunciation error:", e)
    



