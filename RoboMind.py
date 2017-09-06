import can
import time
import threading
import struct
import sys

# Индикатор, в случае ошибки завершающий отправку онлайнов
crash = False


# Нумерация типов
DT_NONE = 0
DT_UINT8 = 1
DT_INT8 = 2
DT_UINT16 = 3
DT_INT16 = 4
DT_UINT32 = 5
DT_INT32 = 6
DT_FLOAT = 7
DT_STRING = 8
DT_PTR = 9
DT_BITMASK = 10 # битовая маска,
DT_RAW = 11 # просто байты

# Магическое число (любое число от 0 до 255) для проверки подключения
MagicNumber = 42
                

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


# Проверка наличия устройств, включенные устройства отвечают на эту команду
def IsAnybodyHere():
    self.bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan_native')  
    AskMsg = can.Message(arbitration_id = 0x500, extended_id = False, data = []) 
    self.bus.send(AskMsg)
    





#### CONTROLLERS

# Базовый контроллер. В него вписывается то, что является общим для всех контроллеров
class ControllerBase():    

    def __init__(self, canAddr):

        # Статус подключения
        self.isConnected = False
        
        # Список параметров
        self.ParamList = {0x00:['Test Param', DT_UINT8]}
        
        # Список команд
        self.CommandList = {
                # Команды управления
                 # name, type, length
            0xC8:['send parametr', DT_UINT8],
            0xC9:['send parameters'],
            0xCA:['write in EEPROM'],
            0xCB:['read from EEPROM'],
                        }

        # Адресс устройства
        self.CanAddr = canAddr

        # Функции обратного вызова
        self.onGetParam = None # При принятии параметра вызывается функция onGetParam, если она определена пользователем
        self.onSetParam = None # При задании параметра
        self.onSendCommand = None # При даче команды

        self.callbacksList = None # Список калбэков
        
        self.exit = False
        
        # Подключаемся к шине
        self.Bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan_native')  

        self.StartRecv()    # Запускаем поток прослушивания шины
    
        self.CheckConnection()  # Выполняем проверку соединения 


    # Работа со словарем параметров

    def GetStructParam(self, prmType):    # Выявляем длину и структуру параметра запрошенного типа

        prmLength = -1
        
        if prmType == (DT_UINT8 or DT_BITMASK):
            prmStruct = struct.Struct('=2B B')
            prmLength = 1
                
        elif prmType == DT_INT8:
            prmStruct = struct.Struct('=2B b')
            prmLength = 1

        elif prmType == DT_UINT16:
            prmStruct = struct.Struct('=2B H')
            prmLength = 2

        elif prmType == DT_INT16:
            prmStruct = struct.Struct('=2B h')
            prmLength = 2

        elif prmType == DT_UINT32:
            prmStruct = struct.Struct('=2B L')
            prmLength = 4

        elif prmType == DT_INT32:
            prmStruct = struct.Struct('=2B l')
            prmLength = 4

        elif prmType == DT_FLOAT:
            prmStruct = struct.Struct('=2B f')
            prmLength = 4

        else:
            print('Неизвестный тип параметра:%d' % prmType)
            # нужно прервать функцию
        
        '''elif prmType == DT_STRING:
            prmStruct = struct.Struct('=2b p')
            prmLength = 0

        elif prmType == DT_RAW:
            prmStruct = struct.Struct('=2b p')
            prmLength = 0

        elif prmType == DT_NONE:
            print('ERROR: prmType = DT_NONE')'''
            
        return(prmStruct, prmLength)


    def SetParam(self, prmNumber, value):   # Отправляем параметр на контроллер
        if self.ParamList.get(prmNumber) != None:  # Существует ли параметр в списке параметров
            prmType = self.ParamList[prmNumber][1]
            prmStruct, prmLength = self.GetStructParam(prmType) # Формируем структуру и длину параметра

            # Для параметров типа стринг, рав и нон
            '''if prmLength == 0:  # Если значение длины параметра равно нулю, значит длину нужно определить особым способом 
                if prmType = DT_STRING: # Если тип параметра строковый
                    prmLength = len(value)
                    if prmLength > 6: # Если в строке больше 6 символов
                        value = value[:6] # Обрезаем строку до 6 символов
                        prmLength = 6
                    prmStruct = struct.Struct('=2b p')    
                else:   # Когда prmType = DT_RAW
            '''        
                    
                    
            packedPrm = prmStruct.pack(prmNumber, prmLength, value)
            packedMessage = can.Message(arbitration_id = self.CanAddr,
                                        extended_id = False,       
                                        data = packedPrm)
            self.Send(packedMessage)

            # Обработчик событий
            if self.onSetParam != None:
                self.onSetParam(prmNumber, value)
            
        else:
            print('Can`t found param with that number:%d' % prmNumber)


            
    # Работа со словарем команд
    
    def GetStructCommand(self, cmdNumber):  # Функция определяющая структуру и длину команды
        structString = ('=B')
        
        for cmdParamType in self.CommandList[cmdNumber][1:]:

            if cmdParamType == DT_UINT8:
                structString = structString + (' B')
                        
            elif cmdParamType == DT_INT8:
                structString = structString + (' b')

            elif cmdParamType == DT_UINT16:
                structString = structString + (' H')

            elif cmdParamType == DT_INT16:
                structString = structString + (' h')

            elif cmdParamType == DT_UINT32:
                structString = structString + (' I')

            elif cmdParamType == DT_INT32:
                structString = structString + (' i')

            elif cmdParamType == DT_FLOAT:
                structString = structString + (' f')

        print(structString)
        cmdStruct = struct.Struct(structString)
        return(cmdStruct)
           

    def SendCommand(self, cmdNumber, cmdParams = None):   # Отправляем комманду на контроллер
        
        if self.CommandList.get(cmdNumber) != None:  # Существует ли команда в словаре команд

            cmdStruct = self.GetStructCommand(cmdNumber) # Узнаем структуру, длину команды и кол-во параметров
            Cmd = (cmdNumber,) + cmdParams
            packedCmd = cmdStruct.pack(*Cmd)
            packedMessage = can.Message(arbitration_id = self.CanAddr,
                                        extended_id = False,       
                                        data = packedCmd)
            self.Send(packedMessage)
            
            # Обработчик событий
            if self.onSendCommand != None:
                self.onSendCommand(*Cmd)

        else:
            print('Can`t found command with that number:%d' % cmdNumber)        

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

    def CheckConnection(self):
        try:
            self.ParamList[0x00][2] = 0 # Обнуляем параметр проверки связи если он есть
        except:
            pass
            
        self.isConnected = False
        self.SetParam(0x00, MagicNumber)  # Задаем тестовый параметр для проверки подключения       
   
    # Функция запускаемая в потоке. Отвечает за прием сообщений
    def ThreadRecv(self):
        global crash

        while not (self.exit or crash):
            inMsg = self.Recv()                      # Получение сообщения

            if inMsg.arbitration_id == (self.CanAddr + 0xFF):
                prmNumber = inMsg.data[0]

                if self.ParamList.get(prmNumber) != None:  # Существует ли параметр в списке параметров
                    prmLengthRecv = inMsg.data[1]

                    #if inMsg.dlc == prmLengthRecv + 2:  # Два байта занято номером параметра и значением длины
                    if True:
                        if inMsg.dlc > prmLengthRecv + 2:
                            inMsg.data = inMsg.data[0:(prmLengthRecv + 2)]
                        prmStruct, prmLength = self.GetStructParam(self.ParamList[inMsg.data[0]][1])   # Выявление структуры и длины для данного типа сообщения

                        if prmLength == prmLengthRecv:  # Длина принятого параметра соответствует длине параметра в парам листе 
                            unpackedPrm = prmStruct.unpack(inMsg.data)
                            try:
                                self.ParamList[prmNumber][2] = unpackedPrm[2] # Пробуем записать полученное значение параметра в список параметров
                            except:
                                self.ParamList[prmNumber].append(unpackedPrm[2]) # Добавляем элемент в список параметров, если его еще не существует

                            if (prmNumber == 0x00) and (self.ParamList[0x00][2] == MagicNumber) and (self.isConnected == False): # Проверка соединения
                                self.isConnected = True
                                print('Device connected')

                            # Обработчик событий

                            if self.onGetParam != None:
                                self.onGetParam(prmNumber, self.ParamList[prmNumber][2])

                                
                            #print('Param recieved. Name:%s  Value:%s' % (self.ParamList[prmNumber][0], str(self.ParamList[prmNumber][2])))
                            
                        else:
                            print('Recieved length not according with recieving type')

                    else:
                        print('Recieved dlc not according with data length')


                else:
                    print('Попытка принять неизвестный параметр:%d' % prmNumber)
                
    def StartRecv(self):
        RecvThread = threading.Thread(target = self.ThreadRecv)
        RecvThread.start()
        self.StartRecv = self.Vacuum                

    # Для блокирования доступа к ф-ии присваиваем ей значение пустой функции
    def Vacuum(self):
        pass

    # Скрытая Фишка
    def FootPrint(self):
        print('AAAAAPCHI')

# Контроллер моторов
class ControllerMotor(ControllerBase):    

    def __init__(self, addr = 0):
        print("addr: %d" % addr)
        try:
            # Возможные адреса лежат в диапазоне 0-8
            assert(0 <= addr < 9), ("ERROR adress controller")
            ControllerBase.__init__(self, 0x200 + addr)      
        except:            
            global crash
            print("Crashed")
            crash = True
            sys.exit(1)
            
        # Дополняем словарь команд
        self.CommandList.update({   
                        # Команды управления
                  # name, type, length
            0xCC:['work mode', DT_UINT8], # пример. Переделать в списки. Название - тип. Параметр задавать не текстом, а номером.
            0xCD:['clear odometres'],
            0xCE:['PWM pulse'],    # Не известно
            0xCF:['set PWM', DT_UINT8, DT_INT16],
            0xD0:['set speed', DT_INT8, DT_INT16],
            0xD1:['set all PWM', DT_INT16, DT_INT16],
            0xD2:['set all speed', DT_INT16, DT_INT16],
            0xD3:['power out', DT_UINT8, DT_UINT8]

                       })

        # Дополняем словарь параметров
        self.ParamList.update({
                # Параметры для чтения и записи
            # name, type, (data)
            0x01:['debug info mask', DT_UINT8],
            0x02:['proportional coefficient', DT_FLOAT],
            0x03:['integral coefficient', DT_FLOAT],
            0x04:['derivative coefficient', DT_FLOAT],
            0x05:['limit summ', DT_INT16],
            0x06:['time PID', DT_UINT16],
            0x07:['time PWM', DT_UINT16],
            0x08:['pwm DeadZone', DT_UINT8],
            0x09:['accelbreak step', DT_UINT8],
            0x0A:['emergency level', DT_UINT16],

                    # Параметры только для чтения

            0x13:['Error Code', DT_UINT8],
            0x14:['Work mode', DT_UINT8],

            # 1 
                       
            0x15:['pParrot1', DT_FLOAT],
            0x16:['iParrot1', DT_FLOAT],
            0x17:['dParrot1', DT_FLOAT],
            0x18:['res PWM1', DT_INT16],
            0x19:['current Parrot1', DT_INT16],
            0x1A:['encoder Data1', DT_INT32],
            0x1B:['Int summ1', DT_INT16],
            0x1C:['adc Average1', DT_UINT16],
            0x1D:['set Parrot1', DT_INT16],
            0x1E:['set PWM1', DT_INT16],

            # 2 
                       
            0x1F:['pParrot2', DT_FLOAT],
            0x20:['iParrot2', DT_FLOAT],
            0x21:['dParrot2', DT_FLOAT],
            0x22:['res PWM2', DT_INT16],
            0x23:['current Parrot2', DT_INT16],
            0x24:['encoder Data2', DT_INT32],
            0x25:['Int summ2', DT_INT16],
            0x26:['adc Average2', DT_UINT16],
            0x27:['set Parrot2', DT_INT16],
            0x28:['set PWM2', DT_INT16],
                       
                      })

      
    def SetWorkMode(self, workMode = 0):        # Инициализация режима работы (2 - ШИМ, 1 - включить ручной режим, 0 - пока используется как выключение ручного режима)
        self.SendCommand(0xCC, (workMode,))
        
    def SetAllSpeed(self, speed1, speed2): # Установить скорость мотора (0 и 1)
        self.SendCommand(0xD2, (speed1, speed2))

    def SetSpeed(self, motorNumber, speed): # Установить скорость мотора (0 и 1)
        self.SendCommand(0xD0, (motorNumber, speed))


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
