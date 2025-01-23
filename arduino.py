from jikko.jikko import *
import requests
import pygame
import time
import datetime


# Jikko 라이브러리를 사용하여 환경 설정
jk = Pyjikko()
PORT = "COM12"
jk.serial_connect(PORT)
jk.start()
jk.lcd_set(0x27, 16, 2)
jk.mp3_set(10, 11)
jk.mp3_volume(30)

# 초기 변수 설정0
cds_pin = A0  # 조도 센서 핀
soil_pin = A1  # 토양수분 센서 핀
soil_std_data = 400  # 토양의 수분량 기준
cds_std_data = 300  # 조도 센서의 빛 세기 기준

cds_datas = [jk.soil_read(cds_pin)] * 3  # 10초 전까지의 조도센서값 가져오기
soil_datas = [jk.soil_read(soil_pin)] * 3  # 10초 전까지의 토양수분값 가져오기

is_say_hello = [False] * 24  # 시간대에 인사를 했는지 여부

cur_time = [0,0,0]

def convert_temp(temp_k):
    # 온도를 Kelvin에서 Celsius로 변환
    return temp_k - 273.15


def read_sensor_values(jk, cds_pin, soil_pin):
    # Jikko 라이브러리를 사용하여 조도와 토양 수분 상태 읽기
    cds_data = jk.cds_read(cds_pin)
    soil_data = jk.soil_read(soil_pin)
    return cds_data, soil_data


def display_sensor_values(jk, cds_data, soil_data):
    # Jikko 라이브러리를 사용하여 LCD에 조도와 토양 수분 상태 표시
    jk.lcd_display(0, 0, f"CDS: {cds_data}")
    jk.lcd_display(0, 1, f"Soil: {soil_data}")
    time.sleep(1)
    jk.lcd_clear()



####상황에 맞게끔 인사하는 mp3파일 재생####
def say_hello(n):
    print(f"지금은 {n}시네요")
    jk.mp3_play_time(2, 3)

def say_thankyou(n):
    print("물주셔서감사합니다")
    jk.mp3_play_time(0, 3)


def check_say_hello(n):
    # 오늘 이 시간에 인사했다면 하지 않기
    if is_say_hello[n]:
        return
    # 인사하고 인사했음을 표시
    say_hello(n)
    is_say_hello[n] = True
    


# 날짜가 지나면 남은 변수들 초기화
def init_values():
    is_say_hello = [False] * 24


# 아침에 불켜질 때 조도 센서 체크
def check_cds_morning(datas):
    gap = datas[-1] - datas[0]
    if gap > cds_std_data:  # 조도센서가 많이 변했다면
        check_say_hello(cur_time[0])  # 그 시간에 맞는 인사하기
        jk.mp3_play_time(3, 3)


def check_cds_night(datas):
    gap = datas[0] - datas[-1]
    if gap > cds_std_data:  # 조도센서가 많이 변했다면
        check_say_hello(cur_time[0])  # 그 시간에 맞는 인사하기
        jk.mp3_play_time(5, 3)


def check_soil(datas):
    gap = datas[0] - datas[-1]
    if gap > soil_std_data:  # 토양수분 센서가 많이 변했다면
        say_thankyou(cur_time[0])  # 감사합니다 말하기


def main():

    cur_time = [datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second]  # 현재 시간
    watered_time = cur_time  # 물 준 시간

    # 날짜가 지나면 초기화 하기위해서 이전 날짜와 함께 저장
    pre_date = datetime.datetime.now().date()
    cur_date = datetime.datetime.now().date()

    while True:
        now = datetime.datetime.now()
        
        if cur_time[0] == 22:
            time.sleep(28000)  # 밤 10시가 되면 아침 6시까지 sleep

        # 센서 값 읽기 및 표시
        cds_data, soil_data = read_sensor_values(jk, cds_pin, soil_pin)
        display_sensor_values(jk, cds_data, soil_data)

        # 현재 시간 받아오기 (시, 분, 초)
        cur_time = [now.hour, now.minute, now.second]
        print(cur_time, cds_data, soil_data)

        # 1분마다 현재 날짜 받아오고 하루가 지났다면 값들 초기화
        if cur_time[2] == 0:
            cur_date = now.date()
            if pre_date != cur_date:
                init_values()  # 변수들 초기화하는 함수
                pre_date = cur_date

        # 조도센서 값 업데이트
        cds_datas.pop(0)
        cds_datas.append(cds_data)
        if 6 <= cur_time[0] <= 9:
            check_cds_morning(cds_datas)
        elif 18 <= cur_time[0] <= 21:
            check_cds_night(cur_datas)

        # 토양 수분 센서 업데이트
        soil_datas.pop(0)
        soil_datas.append(soil_data)
        check_soil(soil_datas)
        
        


if __name__ == "__main__":
    main()
