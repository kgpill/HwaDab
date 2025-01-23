#codig=<utf-8>
from flask import Flask, render_template, request, send_from_directory
from gtts import gTTS
import speech_recognition as sr
import openai
import os
import atexit
import uuid  # 랜덤 파일 이름을 생성하기 위한 모듈

app = Flask(__name__)

# 경로 설정
static_dir = os.path.join(app.root_path, 'static')
mp3_extension = '.mp3'  # 삭제할 파일 확장자
# ChatGPT API 키 설정
api_key = ""
openai.api_key = api_key

# MP3 파일 저장 디렉토리
mp3_dir = os.path.join(app.root_path, 'static')

if os.path.exists(static_dir):
    for filename in os.listdir(static_dir):
        file_path = os.path.join(static_dir, filename)
        try:
            if os.path.isfile(file_path) and file_path.endswith(mp3_extension):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")



@app.route('/')
def home():
    return render_template('index.html')

@app.route("/ask", methods=['GET', 'POST'])
def recognize_speech():
    if request.method == 'POST':
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("질문을 해주세요!")
            audio = r.listen(source)

        try:
            question = r.recognize_google(audio, language="ko-KR")
            print("Google Speech Recognition thinks you said " + question)
            if question:
            # ChatGPT에 질문 보내기
                response = openai.Completion.create(
                    engine="gpt-3.5-turbo-instruct",
                    #prompt=f"'{question}'에 대해 존댓말(-에요 말투로 ex: 안녕하세요)로 답변:",
                    prompt=f"{question}에 대해서 대화형 챗봇(모델명:화답(usup에서 개발한 말하는 스마트 화분(습도 측정, 조도 측정 등 측정하여 요구사항을 직접 말하고 시간에 맞춰 먼저 말을 걸어주는 기능, 사용자의 요구에 대답을 해주는 기능)))으로 0자~100자 이내로 존댓말을 사용해서 작성해줘(꼭 길 필요는 없어):",
                    max_tokens=500,  # 원하는 답변의 최대 길이
                    stop=None  # 답변 종료 문자열 설정
                )
                answer = response.choices[0].text.strip()

                # 랜덤한 파일 이름 생성
                mp3_filename = str(uuid.uuid4()) + '.mp3'
                mp3_path = os.path.join(mp3_dir, mp3_filename)

                # gTTS를 사용하여 문자열을 MP3로 변환
                tts = gTTS(text=answer, lang='ko') 
                tts.save(mp3_path)  # MP3 파일로 저장
                return render_template('index.html', question=question, answer=answer, mp3_url=f'/static/{mp3_filename}')
            else:
                return render_template('index.html', question="음성 인식에 실패했습니다.")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return render_template('index.html', question=question)
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}").format(e)
            return render_template('index.html', question="음성 인식에 실패했습니다.")

if __name__ == '__main__':
    # 개발 서버를 외부에서 접속 가능하도록 설정
    app.run(host='0.0.0.0', port=8080, debug=True)