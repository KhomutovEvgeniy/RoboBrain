from RoboMind import*
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):    # Что происходит при коннекте
    print("Connected with result code: "+str(rc))
    client.subscribe("robot/#", 0) # Подписываемся на все подтопики топика robot

def on_message(client, userdata, message):  # Что происходит при получение сообщения
    #print("Received message '" + str(message.payload) + "' on topic '"
    #    + message.topic + "' with QoS " + str(message.qos))
    pass

def LeftSpeed_callback(client, userdata, message):  # Что происходит при получении сообщения в топик robot/motor-L/speed
    leftSpeed=(int(message.payload))        # Вытаскиваем значение скорости из топика и присваиваем его переменной
    M.SetMotorSpeed(0, leftSpeed)     # Отправляем полученное значение скорости на мотор

def RightSpeed_callback(client, userdata, message):   # Что происходит при получении сообщения в топик robot/motor-R/speed
    rightSpeed = (int(message.payload))          # Вытаскиваем значение скорости из топика и присваиваем его переменной
    M.SetMotorSpeed(1, rightSpeed)   # Отправляем полученное значение скорости на мотор


O = Onliner()
O.online = True
time.sleep(2)
M = ControllerMotor()
M.Mode(1)

client = mqtt.Client()
client.connect("127.0.0.1", 1883, 60)
client.on_connect = on_connect
client.on_message = on_message
client.message_callback_add("robot/motor-R/speed", RightSpeed_callback) # Добавляем калбэк
client.message_callback_add("robot/motor-L/speed", LeftSpeed_callback)  # Добавляем калбэк
client.loop_start()
time.sleep(300)
M.Mode(0)
O.exit = True
client.loop_stop()

