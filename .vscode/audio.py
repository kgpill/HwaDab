#codig=<utf-8>
from flask import Flask, render_template, request, send_from_directory
from gtts import gTTS
import speech_recognition as sr
import openai
import os
import atexit
import uuid  # 랜덤 파일 이름을 생성하기 위한 모듈

app = Flask(__name__)

r=sr.Recognizer()
with sr.Microphone() as source:
        print("Say something!")
        audio=r.listen(source)
try:
        transcript=r.recognize_google(audio, language="ko-KR")
        print("Google Speech Recognition thinks you said "+transcript)
except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template('index.html', transcript=transcript)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)