import can
import time
import struct
import threading
import sys
crash=False

#### KOSTYIL PRODUCTION

class Onliner(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self) # Наследуем поточный класс
        self.online_flag = False        # Онлайн флаг. Если True, то онлайны шлются, если False - не шлются
        self.EXIT = False               # Выход он и есть выход
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan_native')  


    def run(self):              # Функция запускаемая методом self.start()
        global crash
        while not (self.EXIT or crash) :    # Цикл проверки онлайн флага и отправки онлайн метки
            if self.online_flag:
                self.Send_online()
                print("online")
            else:
                time.sleep(1)

    def Send_online(self):      # Отправка онлайн метки
        online_msg = can.Message(arbitration_id=0x600, extended_id=False, data=[]) # Преобразование сообщения в нужную форму (can frame)
        self.bus.send(online_msg)
        time.sleep(1)


#### CONTROLLERS
    
class Base_Controller():    # Базовый контроллер. В него вписывается то, что является общим для всех контроллеров

    def __init__(self, can_addr):

        self.can_addr = can_addr
        self.EXIT = False
        
        ## Подключаемся к шине
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan_native')  

    ## Отправка сообщения в шину
    def Send(self, msg):
        try:
            self.bus.send(msg)       # Библиотечная функция отправки сообщения
#            time.sleep(0.05)
        except OSError:
            print("Sending error")
            time.sleep(1)

    ## Получение сообщения из шины
    def Recv(self):
        try:
            msg = self.bus.recv()    # Библиотечная функция получения сообщения
        except OSError:
            print("Reciving error")
        return msg

    def Thread_to_recv(self):
        global crash
        can_msg = struct.Struct("=8H")  # Зависит от формата посылаемых сообщений        

        while not (self.EXIT or crash):
            InMsg = self.Recv()
            self.recv_msg = can_msg.unpack(InMsg.data)
            print(1)

    def Start_recv(self):
        th = threading.Thread(target = Thread_to_recv)
        th.start()
        self.Start_recv = self.Vacuum                

    ## Для блокирования доступа к ф-ии присваиваем ей значение vacuum

    def Vacuum(self):
        pass

    ## Скрытая Фишка
    def FootPrint(self):
        print('AAAAAPCHI')

class Motor_Controller(Base_Controller):    # Контроллер моторов

    def __init__(self, addr = 0):
        try:
            assert(0<=addr<9), ("ERROR adress controller")
            Base_Controller.__init__(self, 0x200+addr)      # Наследуем базовый контроллер
        except:            
            global crash
            print("Crashed")
            crash=True
            sys.exit(1)
        
    def Mode(self, work_mode = 0):        # Инициализация режима работы (2 - ШИМ, 1 - включить ручной режим, 0 - пока используется как выключение ручного режима)
        
        init_message = can.Message(arbitration_id=self.can_addr, extended_id=False,      # extended_id - фолс - 11 бит, тру - 29 
                      data = [200, work_mode])  
        self.Send(init_message)

    def Set_motor_speed(self, motor_number, speed): # Установить скорость мотора (0 и 1)
        data = self.Pack(motor_number+10, speed)    # Пакуем сообщение, чтобы переслать его в корректном виде
        self.Send(data)  

################## КАК ЗАДАВАТЬ ШИМ? ############
    def Set_motor_PWM(self, motor_number, PWM): 
        pass
#################################################

    def Pack(self, prm_number, prm):                         # Упаковка сообщения
        if ((prm_number == 10) or (prm_number == 11)):       # Если сообщение - установка скорости моторов (10,11)
            typeSpeed = struct.Struct('=2b h')               # Структура сообщения
            packed_data = typeSpeed.pack(prm_number, 2, prm) # Упаковываем сообщение
            packed_message = can.Message(arbitration_id=self.can_addr, extended_id=False,      # extended_id - фолс - 11 бит, тру - 29 
                      data = packed_data)
            return packed_message                            # Возвращаем упакованное сообщение
        else:
            print("Not Packed")

class Stepper_Controller(Base_Controller):

    def __init__(self, addr = 0):

        assert(0<=addr<9), ("ERROR adress controller")

        Base_Controller.__init__(self, 0x230+addr)      # Наследуем базовый контроллер

            
    def Mode(self, work_mode):
        self.Init_Stepper(0,work_mode)
        self.Init_Stepper(1,work_mode)
        self.Init_Stepper(2,work_mode)        
  
        
    def Mode_stepper(self, stepperN, work_mode):    # 2 - рабочий режим
        #self.can_addr = 0x230
        can_msg_init = struct.Struct('=I 7B')
        can_msg_init_data = can_msg_init.pack(self.can_addr, 3, 0, 0, 0, 0xC8, stepperN, work_mode)
        
        self.Send(can_msg_init_data)

    def Calibrate(self, stepperN):
        can_msg_calib_axes = struct.Struct('=I 6B H')
        can_msg_calib_axes_data = can_msg_calib_axes.pack(self.can_addr, 4, 0, 0, 0, 0xCF, stepperN, 0x3C)
        self.Send(can_msg_calib_axes_data)

    def Set_pos(self, stepperN, steps):
        can_msg_stepper_pos = struct.Struct('=I 6B H')
        can_msg_stepper_pos_data = can_msg_stepper_pos.pack(self.can_addr, 4, 0, 0, 0, 0xCE, stepperN, steps)
        self.Send(can_msg_stepper_pos_data)


    def Set_all_pos(self, steps1, steps2, steps3):
        can_msg_steppers_pos = struct.Struct('=I 5B 3H')
        can_msg_steppers_pos_data = can_msg_steppers_pos.pack(self.can_addr, 7, 0, 0, 0, 0xD0, steps1, steps2, steps3)
        self.Send(can_msg_steppers_pos_data)
        
