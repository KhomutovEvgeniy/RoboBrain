import can
import time
import threading
import struct
import sys
from ParamLists import *

# Индикатор, в случае ошибки завершающий отправку онлайнов
crash = False

#### KOSTYIL PRODUCTION

class Onliner(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self) # Наследуем поточный класс
        self.online = False         # Если True, то онлайны шлются, если False - не шлются
        self.exit = False               # Выход он и есть выход

        # Объявляем переменную отвечающую за шину can0
        self.bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan_native')  
        self.start()
    ## Функция с циклом проверки онлайн флага и отправки онлайн метки
    def run(self):              
        global crash
        while not (self.exit or crash):    
            if self.online:
                self.SendOnline()
                print("online")
            time.sleep(1)

    ## Отправка онлайн метки
    def SendOnline(self):      
        # Формируем сообщение
        onlineMsg = can.Message(arbitration_id = 0x600, extended_id = False, data = []) 
        self.bus.send(onlineMsg)
        


#### CONTROLLERS

# Базовый контроллер. В него вписывается то, что является общим для всех контроллеров
class ControllerBase():    

    def __init__(self, canAddr):

        # Лист параметров
        self.ParamList = {}

        # Адресс устройства
        self.CanAddr = canAddr
        
        self.exit = False
        
        # Подключаемся к шине
        self.Bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan_native')  

    # Работа с парамлистом
    
    # Отправка сообщения в шину
    def Send(self, msg):
        try:
            self.Bus.send(msg)       # Библиотечная функция отправки сообщения
        except OSError:
            print("Sending error")
            time.sleep(1)

    # Получение сообщения из шины
    def Recv(self):
        try:
            msg = self.Bus.recv()    # Библиотечная функция получения сообщения
        except OSError:
            print("Reciving error")
        return msg

    # Функция запускаемая в потоке. Отвечает за прием сообщений
    def ThreadRecv(self):
        global crash
        CanMsg = struct.Struct("=8H")  # Формат посылаемых сообщений        

        while not (self.exit or crash):
            inMsg = self.Recv()                      # Получение сообщения
            self.recvMsg = CanMsg.unpack(inMsg.data) # Распаковка сообщения

    def StartRecv(self):
        RecvThread = threading.Thread(target = ThreadRecv)
        RecvThread.start()
        self.StartRecv = self.Vacuum                

    # Для блокирования доступа к ф-ии присваиваем ей значение пустой функции

    def Pack(self):                         # Упаковка сообщения
        return Handlerissimo(self)
        

    def Vacuum(self):
        pass

    # Скрытая Фишка
    def FootPrint(self):
        print('AAAAAPCHI')

# Контроллер моторов
class ControllerMotor(ControllerBase):    

    def __init__(self, addr = 0):
        try:
            # Возможные адреса лежат в диапазоне 0-8
            assert(0 <= addr < 9), ("ERROR adress controller")
            ControllerBase.__init__(self, 0x200 + addr)      
        except:            
            global crash
            print("Crashed")
            crash = True
            sys.exit(1)
        
    def Mode(self, workMode = 0):        # Инициализация режима работы (2 - ШИМ, 1 - включить ручной режим, 0 - пока используется как выключение ручного режима)
        
        initMessage = can.Message(arbitration_id = self.CanAddr, extended_id = False,      # extended_id - фолс - 11 бит, тру - 29 
                                  data = [200, workMode])  
        self.Send(initMessage)

    def SetMotorSpeed(self, motorNumber, speed): # Установить скорость мотора (0 и 1)
        self.motorNumber, self.speed, self.prmNumber = motorNumber, speed, 0xCF
        
        data = self.Pack()    # Пакуем сообщение, чтобы переслать его в корректном виде
        self.Send(data)  

################## КАК ЗАДАВАТЬ ШИМ? ############
    def SetMotorPWM(self, motorNumber, PWM): 
        pass
#################################################



### Не используется в связи с не готовностью
            
class ControllerStepper(ControllerBase):

    def __init__(self, addr = 0):

        assert(0 <= addr < 9), ("ERROR adress controller")

        ControllerBase.__init__(self, 0x230+addr)      # Наследуем базовый контроллер

            
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
        
