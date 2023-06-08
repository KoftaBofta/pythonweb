from flask import Blueprint, render_template, request, flash, redirect, session, url_for,jsonify, make_response
import pyttsx3
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import ssl
import smtplib
import imaplib
from email.message import EmailMessage
import email
import speech_recognition as sr
from gtts import gTTS
from translate import Translator
from playsound import playsound
import winsound
from threading import Thread
import threading
import time
import os
import re

        
email_sender = 'hotmailsendmessage@gmail.com'
email_password= 'czrcrgsuxiycvrok'
email_receiver= 'mandosegua@gmail.com'
voice_running = "stopped"

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

def arabicread(text):
    placetoplay = 'hello.mp3'
    tts = gTTS(text=text, lang='ar', slow=False)
    tts.save(placetoplay)
    playsound(placetoplay)
    os.remove(placetoplay)
    return

def convert_characters(unprocesedbody):
    body = unprocesedbody.lower()
    body1 = body.replace("comma",",")
    body2 = body1.replace("slash","/")
    body3 = body2.replace("dot",".")
    body4 = body3.replace("question mark","?")
    body5 = body4.replace("exclamation mark","!")
    return body5

def speak(duration):
    with sr.Microphone() as src:
        audio = r.record(src, duration=duration)
        try:
            mytext = r.recognize_google(audio)
        except:
            mytext = 'Did not work'
        return mytext
    
def identify_email():
    hellop = Thread(target=texttospeech, args=("Please State Your Email",)).start()
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

def compose_email(reciever, subject, content):
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = reciever
    em['Subject'] = subject
    em.set_content(content)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        try:
            smtp.sendmail(email_sender, reciever, em.as_string())
        except:
            failure = "hello"
    if 'recepient' in session:
        session['recepient'] = ""
    if 'replyingbody' in session:
        session['replyingbody'] = ""
    return

def open_inbox(x,y,which):
    
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    
    imap.login(email_sender, email_password)
    imap.select(which)
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


    
@auth.route('/sign_up', methods=['GET','POST'])
def sign_up():
    print(request.args)
    if request.method == "POST":
        addr = request.form.get('addr')
        passw = request.form.get('passw')
        numpass = request.form.get('num_pass')
        entry = User.query.filter_by(email = addr).first()
        if entry:
            print("EXISTS!!!!!!!!!!!!!!!!!!!!")
        else:
            new_entry = User(email=addr, password = passw, numerical_password = generate_password_hash(numpass, method='sha256'))
            db.session.add(new_entry)
            db.session.commit()
        
    return render_template("sign_up.html")




@auth.route('/login', methods=['GET','POST'])
def login():
    entries = User.query.all()
    for entry in entries:
        print("AN ENTRYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
        print(entry.email)
    email_authenticated=False
    password_authenticated=False
    email=""
    password=""
    print(request.args)
    id=request.args.get("id")
    if id=="login" and request.method == 'POST':
        passw = request.form.get('password')
        print(passw)
        valid_entry = ""
        entries = User.query.all()
        for entry in entries:
                if check_password_hash(entry.numerical_password, passw):
                    valid_entry = entry
        if valid_entry != "":
            print("success!!!!!!!!!!!!!")
        else:
            print("EPIC FAIL!!!!!!!!!!!!!!")
    if id=="listen":
            email = identify_email()
            email = turnintoemail(email)
            print(email)
            texttospeech("Your email is")
            texttospeech(email)
            password = identify_password()
            password.replace(" ", "")
            print(password)
            texttospeech("Your password is")
            texttospeech(password)
        
    return render_template("login.html")


@auth.route('/logout')
def logout():
    return "<p>Logout</p>"


@auth.route('/',  methods=['GET', 'POST'])
def home():
    session['page'] = 0
    session['pagespam'] = 0
    session['voice'] = "stopped"
    if request.method== 'POST':
        texttospeech("where do you wish to go?")
        location = speak(10)
        print(location)
        if location == "log in":
             return redirect("/login")
        elif location == "sign up":
            return redirect("/sign_up")
    return render_template("home.html")


@auth.route('/inbox',  methods=['GET', 'POST'])
def inbox():
    input_value = request.form.get('inputValue')
    print(input_value)
    print('in inbox its')
    print(session['voice'])
    id=request.args.get("id")
    if id=="next":
        session['page'] = session['page'] + 5
    if id=="previous":
        if(session['page'] != 0) :
            session['page'] = session['page'] - 5
    x = session['page']
    inbox = open_inbox(x, x + 5, "inbox")
    if id=="listen" and request.method == "POST":
        session['voice'] = "running"
        x = 0
        for row in inbox:
            texttospeech("Email by")
            texttospeech(row[0])
            texttospeech("would you like to read this email?")
            confirm = speak(5)
            if "read" in confirm or "message" in confirm:
                tbr = row[2]
                texttospeech("would you like to translate this email")
                translateconfirm = speak(5)
                if "translate" in translateconfirm or "message" in translateconfirm:
                    trans= Translator(to_lang="ar")
                    abr = trans.translate(tbr)
                    arabicread(abr)
                else:
                    texttospeech(tbr)
                texttospeech("would you like to reply?")
                replyreq = speak(8)
                if "reply" in replyreq or "message" in replyreq:
                    mailrecipient1 = re.search(r'<(.+?)>', row[0])
                    mailrecipient = mailrecipient1.group(1)
                    session['recepient'] = mailrecipient
                    print("recepient is")
                    print(session['recepient'])
                    session['replyingbody'] = row[2]
                    return redirect("/compose")
            x = x + 1
        session['voice'] = "stopped"
    
    return render_template("inbox.html", inbox=inbox)


@auth.route('/spam',  methods=['GET', 'POST'])
def spam():
    id=request.args.get("id")
    if id=="next":
        session['pagespam'] = session['pagespam'] + 5
    if id=="previous":
        if(session['pagespam'] != 0) :
            session['pagespam'] = session['pagespam'] - 5
    x = session['pagespam']
    spam = open_inbox(x, x + 5, "[Gmail]/Spam")
    if id=="listen" and request.method == "POST":
        session['voice'] = "running"
        x = 0
        for row in spam:
            texttospeech("Email by")
            texttospeech(row[0])
            texttospeech("would you like to read this email?")
            confirm = speak(5)
            if "read" in confirm or "message" in confirm:
                tbr = row[2]
                texttospeech("would you like to translate this email")
                translateconfirm = speak(5)
                if "translate" in translateconfirm or "message" in translateconfirm:
                    trans= Translator(to_lang="ar")
                    abr = trans.translate(tbr)
                    arabicread(abr)
                else:
                    texttospeech(tbr)
                texttospeech("would you like to reply?")
                replyreq = speak(8)
                if "reply" in replyreq or "message" in replyreq:
                    mailrecipient1 = re.search(r'<(.+?)>', row[0])
                    mailrecipient = mailrecipient1.group(1)
                    session['recepient'] = mailrecipient
                    print("recepient is")
                    print(session['recepient'])
                    session['replyingbody'] = row[2]
                    return redirect("/compose")
        session['voice'] = "stopped"
    
    return render_template("spam.html", spam=spam)


@auth.route('/compose', methods=['GET', 'POST'])
def compose():
    displaymail=""
    displaybody=""
    if 'recepient' in session and session.get('recepient') != "":
        displaymail = session['recepient']
    if 'replyingbody' in session:
        displaybody = "<" + session['replyingbody'] + ">"
    id=request.args.get("id")
    if id=="listen" and request.method == "POST":
        reciever = ""
        if 'recepient' in session and session.get('recepient') != "":
            texttospeech("sending email to")
            texttospeech(session['recepient'])
            texttospeech("would you like to change the recepient?")
            changrep= speak(5)
            if 'change' in changrep or 'recepient' in changrep:
                session["recepient"] = ""
                texttospeech("who should recieve this email")
                reci = speak(4) 
                reciever = reci
            else:
                reciever = session["recepient"]
                session["recepient"] = ""
        else:
            texttospeech("who should recieve this email")
            reci = speak(4)
            reciever = reci
        texttospeech("please identify the subject")
        subj = speak(4)
        texttospeech("please identify the body")
        body = speak(4)
        processed_body = convert_characters(body)
        if 'replyingbody' in session:
            if session['replyingbody'] != "":
                part = "<" + session['replyingbody'] + ">"
                processed_body = part + " " + processed_body
        id2=request.args.get("id2")
        if id2=="shortcut":
            print("i am in id2 ok thank you")
            datap = {
            "reciever" : reciever,
            "subj": subj,
            "body": processed_body
            }
            print(datap)
            return jsonify(datap)
        return render_template("compose.html", reciever=reciever, subj=subj, body=processed_body)
    
    if id=="send":
        formreciever = request.form.get('recepient')
        formsubject = request.form.get('subject')
        formbody = request.form.get('body')
        print("this is reciever")
        print(formreciever)
        if(formreciever != "" and formsubject != "" and formbody != ""):
            if(formreciever != "Did not work"):
                compose_email(formreciever, formsubject, formbody)
        return render_template("compose.html")
    return render_template("compose.html", reciever=displaymail, body=displaybody)


@auth.route('/navigate', methods=['GET','POST'])
def navigate():
    if request.method == "POST":
        texttospeech("Would you like to go to inbox?")
        response1=speak(5)
        if 'go' in response1 or 'location' in response1:
            return redirect("/inbox")
        texttospeech("Would you like to go to compose?")
        response2=speak(5)
        if 'go' in response2 or 'location' in response2:
            return redirect("/compose")
        texttospeech("Would you like to go to spam?")
        response3=speak(5)
        if 'go' in response3 or 'location' in response3:
            return redirect("/spam")
        return redirect("/inbox")
    return redirect("/inbox")