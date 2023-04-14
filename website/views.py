from flask import Blueprint, render_template, request, flash, redirect
import pyttsx3
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os

r = sr.Recognizer()
engine = pyttsx3.init()
auth = Blueprint('auth', __name__)
file="hello"

def texttospeech(text, placetoplay):
    placetoplay = placetoplay + '.mp3'
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(placetoplay)
    playsound(placetoplay)
    os.remove(placetoplay)
    return

def speak():
    with sr.Microphone() as src:
        r.adjust_for_ambient_noise(src,duration=1)
        audio = r.listen(src)
        try:
            mytext = r.recognize_google(audio)
        except:
            mytext = 'Did not work'
        return mytext
    
views = Blueprint('views', __name__)
