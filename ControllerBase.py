import can
import time
import threading
import struct
import sys

#### KOSTYIL PRODUCTION

# Индикатор, в случае ошибки завершающий отправку онлайнов
crash = False

# Магическое число (любое число от 0 до 255) для проверки подключения
MagicNumber = 42
                

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


#### CONTROLLERS

# Базовый контроллер. В него вписывается то, что является общим для всех контроллеров
class ControllerBase():    

    def __init__(self, owner, canAddr, controllerName):

        # Указатель на элемент класса робот
        self.owner = owner

        # Статус подключения
        self.__isConnected = False
        
        # Функции обратного вызова
        self.OnGetParam = None # При принятии параметра вызывается функция BasicOnGetParam, если она определена пользователем
        self.OnSetParam = None # При задании параметра
        self.OnSendCommand = None # При даче команды
        self.BasicOnGetParam = None # При принятии параметра вызывается функция BasicOnGetParam
        # Список параметров
        self.__ParamList = {0x00:['Test connection', DT_UINT8]}

        # Список команд
        self.__CommandList = {
                # Команды управления
                 # name, type, length
            0xC8:['Send param', DT_UINT8],
            0xC9:['Send important params'],
            0xCA:['Write in EEPROM'],
            0xCB:['Read from EEPROM'],
                        }

        # Адресс устройства
        self.CanAddr = canAddr

        # Имя устройства
        self.ControllerName = controllerName

        try:
            self.owner.AddDevice(self)
            self.CheckConnection()  # Выполняем проверку соединения (отвечает ли контроллер на запросы) 
            time.sleep(0.1)  # Даем устройству время для ответа на проверку соединения
        except:
            assert False, 'Error with owner'

    def BasicOnGetParam(self, prmNumber, prm):
        if self.OnGetParam != None:
            self.OnGetParam(prmNumber, prm)
        
        

    def GetIsConnected(self): # Чтение
        return self.__isConnected
        
    isConnected = property(GetIsConnected)

    # Работа со словарем параметров

    def ParamExist(self, prmNumber):
        if self.__ParamList.get(prmNumber) != None:
            return True
        else:
            return False

    def GetParam(self, prmNumber, elementNumber = 2):
        if self.ParamExist(prmNumber):
            try:
                return(self.__ParamList[prmNumber][elementNumber]) # Под номером 2 (3-й элемент списка) лежит само значение параметра
            except:
                print('Uncorrect number of element')
        else:
            print('Param can not be founded')

    def SetParam(self, prmNumber, value):
        if self.ParamExist(prmNumber):
            try:
                self.__ParamList[prmNumber][2] = value
            except:
                self.__ParamList[prmNumber].append(value) # Добавляем элемент в список параметров, если его еще не существует
                # Проверяем не существует ли лишних элементов по заданному ключу. 
                try:
                    self.__ParamList[prmNumber][3] = True
                    print('Error: Param %d have too much params' % prmNumber)
                except:
                    pass

        else:
            print('Param can not be founded')
        
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
            assert False, 'Uncorrect param type:%d' % prmType
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


    def SendParam(self, prmNumber, value):   # Отправляем параметр на контроллер
        if self.__ParamList.get(prmNumber) != None:  # Существует ли параметр в списке параметров
            prmType = self.__ParamList[prmNumber][1]
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

            self.owner.Send(packedMessage)

            # Обработчик событий
            if self.OnSetParam != None:
                self.OnSetParam(prmNumber, value)
            
        else:
            print('Can`t found param with that number:%d' % prmNumber)


            
    # Работа со словарем команд
    
    def GetStructCommand(self, cmdNumber):  # Функция определяющая структуру и длину команды
        structString = ('=B')
        
        for cmdParamType in self.__CommandList[cmdNumber][1:]:

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

        cmdStruct = struct.Struct(structString)
        return(cmdStruct)
           

    def SendCommand(self, cmdNumber, cmdParams = None):   # Отправляем комманду на контроллер
        
        if self.__CommandList.get(cmdNumber) != None:  # Существует ли команда в словаре команд

            cmdStruct = self.GetStructCommand(cmdNumber) # Узнаем структуру, длину команды и кол-во параметров
            Cmd = (cmdNumber,) + cmdParams
            packedCmd = cmdStruct.pack(*Cmd)
            packedMessage = can.Message(arbitration_id = self.CanAddr,
                                        extended_id = False,       
                                        data = packedCmd)
            self.owner.Send(packedMessage)
            
            # Обработчик событий
            if self.OnSendCommand != None:
                self.OnSendCommand(*Cmd)

        else:
            print('Can`t found command with that number:%d' % cmdNumber)        

        
    def CheckConnection(self):
        try:
            self.__ParamList[0x00][2] = 0 # Обнуляем параметр проверки связи если он есть
        except:
            pass
            
        self.__isConnected = False
        self.SendParam(0x00, MagicNumber)  # Задаем тестовый параметр для проверки подключения       
   
    # Скрытая Фишка
    def FootPrint(self):
        print('AAAAAPCHI')

