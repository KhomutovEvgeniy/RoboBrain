#   qos 0 - сообщение отправляется единажды 
#   qos 1 - сообщение отправляется, если не получен ответ об удачной доставке, отправляется повторно
#   qos 2 - сообщение отправляется единажды, гарантированно доставляется, но медленно

import paho.mqtt.client as mqtt
import time
import pygame

speedL, speedR = 0, 0   # Скорость моторов
lB5 = 0                 # Предыдущее значение кнопки 5

def on_publish(client, userdata, mid):  # При публикации сообщения 
    print("on_publish")             

def Say(value):  # Публикация значения кнопки 5 джойстика в топик robot/voice
    (rc,mid) = client.publish("robot/voice", value, qos=0)

def Normalize(speed):  # Нормализуем скорость (не даем ей преодолевать определенную границу)
    if speed>98:
        speed = 98
    elif speed<-98:
        speed = -98
    return(speed)

pygame.init()               # Запускаем пугейм
joystick = pygame.joystick.Joystick(0)  # Присваиваем первому подключенному джойстику(0) имя "joystick"
joystick.init()             # Инициализируем джойстик "joystick"


client = mqtt.Client()      # Переназначаем имя для упрощения обращения

client.on_publish = on_publish  # Присваиваем функции публикации написанную функцию

client.connect("192.168.42.25", 1883) # Подключаемся к 1883 порту по указанному адрессу

client.loop_start()     # Начало петли 


### Цикл публикации значений с джойстика ###

while True:
    
    pygame.event.get()  # Узнаем о событиях джойстика (изменения положений осей и кнопок)
    if joystick.get_button(5):  # Проверяем пятую кнопку, нажата ли?
        B5 = True
    else:
        B5 = False

###### Обработчик осей стиков ######
        
    h_axs = int(100*joystick.get_axis(2))  # Содержит значение горизонтальной оси правого стика (варируется от -100 до 100)
    v_axs = int(100*joystick.get_axis(1))  # Содержит значение вертикальной оси левого стика

    h_axs = ((h_axs+2)//20)*20                # Преобразуем шаг изменения значения горизонтальной оси с 1 на 20 
    v_axs = ((v_axs+2)//20)*20                # То же с вертикальной осью. Таким образом 200 возможных значений скорости мотора преобразуются в 11

    h_axs = int(h_axs//2)                     # Уменьшаем значение горизонтальной оси в 2 раза, для уменьшения скорости поворота в дальнейшем
    
    if h_axs<=0:
        speedR = (v_axs) - h_axs
        speedL = (v_axs) 
    else:
        speedR = (v_axs)
        speedL = (v_axs) + h_axs

    speedL = Normalize(speedL) # Нормализация значений скорости (не даем им превысить допустимые)
    speedR = Normalize(speedR)
        
    (rc,mid) = client.publish("robot/motor-R/speed", speedR, qos=0) # Публикуем скорости
    (rc,mid) = client.publish("robot/motor-L/speed", -speedL, qos=0)

    if abs(B5-lB5): # Если индикатор кнопки изменился (Зажата/Отжата)
        if B5:  # Если зажата
            Say(B5)  # Отправить команду запуска речи
        lB5 = B5 # Сохраняем значение индикатора кнопки

    time.sleep(0.1) # Задержка в секундах
   
pygame.quit()       # Закрываем пугейм
client.loop_stop()  # Конец петли
