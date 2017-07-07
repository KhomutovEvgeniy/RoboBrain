#   qos 0 - сообщение отправляется единажды 
#   qos 1 - сообщение отправляется, если не получен ответ об удачной доставке, отправляется повторно
#   qos 2 - сообщение отправляется единажды, гарантированно доставляется, но медленно

import paho.mqtt.client as mqtt
import time

def on_publish(client, userdata, mid):  # При публикации сообщения 
    print("on_publish")             

def Say(value):  # Публикация значения кнопки 5 джойстика в топик robot/voice
    (rc,mid) = client.publish("robot/voice", value, qos=0)

client = mqtt.Client()      # Переназначаем имя для упрощения обращения

client.on_publish = on_publish  # Присваиваем функции публикации написанную функцию

client.connect("127.0.0.1", 1883) # Подключаемся к 1883 порту по указанному адрессу

client.loop_start()     # Начало петли 

(rc,mid) = client.publish("robot/motor-R/speed", 20, qos=0) # Публикуем скорости
(rc,mid) = client.publish("robot/motor-L/speed", 20, qos=0)

time.sleep(10) # Задержка в 0,1 с

(rc,mid) = client.publish("robot/motor-R/speed", 0, qos=0) # Публикуем скорости
(rc,mid) = client.publish("robot/motor-L/speed", 0, qos=0)

time.sleep(2) # Задержка в 0,1 с

client.loop_stop()  # Конец петли
