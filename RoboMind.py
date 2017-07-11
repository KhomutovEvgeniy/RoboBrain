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

        # Список параметров
        self.ParamList = {}
        
        # Список команд
        self.CommandList = {}

        # Адресс устройства
        self.CanAddr = canAddr

        self.exit = False
        
        # Подключаемся к шине
        self.Bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan_native')  

        self.StartRecv()    # Запускаем поток прослушивания шины 

    # Работа с парамлистом

    def GetStructParam(self, prmType):    # Выявляем длину и структуру параметра запрошенного типа

        prmLength = -1
        
        if prmType == (DT_UINT8 or DT_BITMASK):
            prmStruct = struct.Struct('=2b B')
            prmLength = 1
                
        elif prmType == DT_INT8:
            prmStruct = struct.Struct('=2b b')
            prmLength = 1

        elif prmType == DT_UINT16:
            prmStruct = struct.Struct('=2b H')
            prmLength = 2

        elif prmType == DT_INT16:
            prmStruct = struct.Struct('=2b h')
            prmLength = 2

        elif prmType == DT_UINT32:
            prmStruct = struct.Struct('=2b L')
            prmLength = 4

        elif prmType == DT_INT32:
            prmStruct = struct.Struct('=2b l')
            prmLength = 4

        elif prmType == DT_FLOAT:
            prmStruct = struct.Struct('=2b f')
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
        

    # Обработчики
    
    def UInt8Int16Handler(self):
        datatype = struct.Struct('=2b B h')              # Структура сообщения
        packedData = datatype.pack(self.prmNumber, 3, self.prm, self.prm2)  # Упаковываем сообщение

        # extended_id - фолс - 11 бит, тру - 29
        packedMessage = can.Message(arbitration_id = self.CanAddr,
                                    extended_id = False,       
                                    data = packedData)
        
        return packedMessage    # Возвращаем упакованное сообщение

    
    def Int16Int16Handler(self):
        datatype = struct.Struct('=2b h h')              # Структура сообщения
        packedData = datatype.pack(self.prmNumber, 4, self.prm, self.prm2)  # Упаковываем сообщение

        # extended_id - фолс - 11 бит, тру - 29
        packedMessage = can.Message(arbitration_id = self.CanAddr,
                                    extended_id = False,       
                                    data = packedData)
        
        return packedMessage    # Возвращаем упакованное сообщение


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

        while not (self.exit or crash):
            inMsg = self.Recv()                      # Получение сообщения

            if inMsg.arbitration_id == (self.CanAddr + 0xFF):
                prmNumber = inMsg.data[0]

                if self.ParamList.get(prmNumber) != None:  # Существует ли параметр в списке параметров
                    prmLengthRecv = inMsg.data[1]

                    if inMsg.dlc == prmLengthRecv + 2:  # Два байта занято номером параметра и значением длины
                        prmStruct, prmLength = self.GetStructParam(self.ParamList[inMsg.data[0]][1])   # Выявление структуры и длины для данного типа сообщения

                        if prmLength == prmLengthRecv:  # Длина принятого параметра соответствует длине параметра в парам листе 
                            unpackedPrm = prmStruct.unpack(inMsg.data)
                            try:
                                self.ParamList[prmNumber][2] = unpackedPrm[2] # Пробуем записать полученное значение параметра в список параметров
                            except:
                                self.ParamList[prmNumber].append(unpackedPrm[2]) # Добавляем элемент в список параметров, если его еще не существует
                            print('Param recieved. Name:%s  Value:%s' % (self.ParamList[prmNumber][0], str(self.ParamList[prmNumber][2])))
                            
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

        '''

        CommandList = {
                                # Команды управления

                              #name, type, length
                       0xC8:['work mode', dtUInt8], # пример. Переделать в списки. Название - тип. Параметр задавать не текстом, а номером.
                       0xC9:['send parameters', dtNone, params],
                       0xCA:['write in EEPROM', dtNone, startPositions],
                       0xCB:['read from EEPROM', dtNone, startPositionsInEEPROM],
                       0xCC:['clear odometres', dtNone, odometr],
                       0xCD:['set PWM for same time', dtUnknown, timePWM],    # Не известно
                       0xCE:['set PWM', dtUInt8Int16, PWM],
                       0xCF:['set speed', dtInt8Int16, speed],
                       0xD0:['set all PWM', dtInt16Int16, allPWM],
                       0xD1:['set all speeds', dtInt16Int16, allSpeeds],
                       0xD2:['power out', dtUInt8, powerStat],

                       }
                       '''


        self.ParamList = {
                                # Параметры для чтения и записи
                                #name, type,(data)
                       0x00:['debug info mask', DT_UINT8],
                       0x01:['proportional coefficient', DT_FLOAT],
                       0x02:['integral coefficient', DT_FLOAT],
                       0x03:['derivative coefficient', DT_FLOAT],
                       0x04:['limit summ', DT_INT16],
                       0x05:['time PID', DT_UINT16],
                       0x06:['time PWM', DT_UINT16],
                       0x07:['pwm DeadZone', DT_UINT8],
                       0x08:['accelbreak step', DT_UINT8],
                       0x09:['emergency level', DT_UINT16],

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
                       
                      }

      
    def Mode(self, workMode = 0):        # Инициализация режима работы (2 - ШИМ, 1 - включить ручной режим, 0 - пока используется как выключение ручного режима)
        
        initMessage = can.Message(arbitration_id = self.CanAddr, extended_id = False,      # extended_id - фолс - 11 бит, тру - 29 
                                  data = [200, workMode])  
        self.Send(initMessage)

    def SetMotorSpeed(self, motorNumber, speed): # Установить скорость мотора (0 и 1)
        prmNumber = 0xcf
        data = self.Pack(prmNumber, motorNumber, speed)    # Пакуем сообщение, чтобы переслать его в корректном виде
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
        
