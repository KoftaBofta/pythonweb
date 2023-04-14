from flask import Blueprint, render_template, request, flash, redirect, session
import pyttsx3
import ssl
import smtplib
import imaplib
from email.message import EmailMessage
import email
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import winsound
import threading
import time
import os
import re

        
email_sender = 'hotmailsendmessage@gmail.com'
email_password= 'czrcrgsuxiycvrok'
email_receiver= 'mandosegua@gmail.com'

r = sr.Recognizer()
engine = pyttsx3.init()
auth = Blueprint('auth', __name__)
auth.secret_key = "hello"
file="hello"
loop_stopper = False

def texttospeech(text):
    placetoplay = 'hello.mp3'
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(placetoplay)
    playsound(placetoplay)
    os.remove(placetoplay)
    return

def speak(duration):
    with sr.Microphone() as src:
        audio = r.record(src, duration=duration)
        try:
            mytext = r.recognize_google(audio)
        except:
            mytext = 'Did not work'
        return mytext
    
def identify_email():
    texttospeech("please state your email")
    email = speak(20)
    email.replace(" ", "")
    email.replace("at","@")
    email.replace("dot", ".")
    return email

def identify_password():
    texttospeech("Please state your password")
    password = speak(20)
    password.replace(" ", "")
    return password

def compose_email(subject, content):
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(content)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    
    return

def open_inbox(x,y):
    
    imap = imaplib.IMAP4_SSL('imap.gmail.com')

    imap.login(email_sender, email_password)
    imap.select('inbox')
    _, response = imap.search(None, 'ALL')
    inbox = []
    i = x
    message_ids = response[0].split()
    if(y > len(message_ids)):
        y = len(message_ids) - 1
    while i <= y:
        _, response = imap.fetch(message_ids[i], '(RFC822)')
        mes = email.message_from_bytes(response[0][1])
        for text in mes.walk():
            if text.get_content_type() == 'text/plain':
                process_text = text.get_payload(decode=True)
                readable= process_text.decode('utf-8')
                no_links = re.sub(r'http\S+', 'link', readable)
                no_links.replace("<", "")
                no_links.replace(">", "")
                inbox.append([mes['From'],mes['Subject'], no_links])
        i = i + 1
        
    return inbox
        



def turnintoemail(text):
    text = text.replace('a t', '@')
    text = text.replace('at', '@')
    text = text.replace('dot', '.')
    text = text.replace(" ", "")
    return text


    





@auth.route('/login', methods=['GET','POST'])
def login():
    email_authenticated=False
    password_authenticated=False
    email=""
    password=""
    print(request.args)
    id=request.args.get("id")
    print("AIGHT BUDDY ITSSSSSS")
    print(session['voice'])
    if id=="listen" and (session['voice']!="running"):
            session['voice'] = "running"
            t = threading.Thread(target=texttospeech, args=("aight buddy it is now running looooooool kinda crazy how that works",))
            t.start()
            t.join()  # Wait for the thread to finish
            texttospeech(session['voice'])
        
    return render_template("login.html", em=email, passw=password)


@auth.route('/logout')
def logout():
    return "<p>Logout</p>"


@auth.route('/',  methods=['GET', 'POST'])
def home():
    session['page'] = 0
    session['voice'] = "stopped"
    if request.method== 'POST':
        texttospeech("where do you wish to go?")
        location = speak(10)
        print(location)
        if location == "log in":
             return redirect("/login")
        elif location == "sign up":
            return redirect("/sign-up")
    return render_template("home.html")


@auth.route('/inbox',  methods=['GET', 'POST'])
def inbox():
    print('in inbox its')
    print(session['voice'])
    id=request.args.get("id")
    if id=="next":
        session['page'] = session['page'] + 5
    if id=="previous":
        if(session['page'] != 0) :
            session['page'] = session['page'] - 5
    x = session['page']
    inbox = open_inbox(x, x + 5)
    if id=="listen" and session['voice'] != "running":
        session['voice'] = "running"
        x = 0
        for row in inbox:
            texttospeech("Email by")
            texttospeech(row[0])
            texttospeech("would you like to read this email?")
            confirm = speak(5)
            if confirm=="yes":
                texttospeech(row[2])
            texttospeech("would you like to reply?")
            replyreq = speak(8)
            if replyreq=="yes":
                session['recepient'] = email_receiver
                return redirect("/compose")
            x = x + 1
        session['voice'] = "stopped"
    
    return render_template("inbox.html", inbox=inbox)


@auth.route('/compose', methods=['GET', 'POST'])
def compose():
    id=request.args.get("id")
    if id=="listen" and session['voice'] != "running":
        session['voice'] = "running"
        reciever = ""
        if 'recepient' in session:
            reciever = session['recepient']
        else:
            texttospeech("who should recieve this email")
            reciever = 'mandosegua@gmail.com'
            session['recepient'] = reciever
        texttospeech("please identify the subject")
        subj = speak(15)
        texttospeech("please identify the body")
        body = speak(30)
        session['voice'] = "stopped"
        return render_template("compose.html", reciever=reciever, subj=subj, body=body)
    if id=="send":
        formreciever = request.form.get('recipient')
        formsubject = request.form.get('subject')
        formbody = request.form.get('body')
        compose_email(formsubject, formbody)
        return render_template("compose.html")
    return render_template("compose.html")