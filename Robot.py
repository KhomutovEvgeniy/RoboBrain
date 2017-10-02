from ControllerMotor import *
from ControllerServo import *
from ControllerStepper import *
import queue

crash = False

class Robot():
    
    def __init__(self, canbus = 'can0'):

        try:
            # Подключаемся к шине
            self.Bus = can.interface.Bus(channel = canbus, bustype = 'socketcan_native')  
        except:            
            global crash
            print("Crashed")
            crash = True
            sys.exit(1)

        # Список устройств
        self.deviceList = []
        
        # Список устройств ответивших на запрос(500 метка)
        self.answeredDeviceList = []

        # Флаг онлайн метки
        self.online = False         # Если True, то онлайны шлются, если False - не шлются

        self.StartRecv()    # Запускаем поток прослушивания шины

        self.StartSendOnline()      # Запускаем поток отправляющий онлайн метку
        
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
      
    # Функция с циклом проверки онлайн флага и отправки онлайн метки, запускается как поток
    def SendOnlineThread(self):              
        global crash
        self.SendOnline()
        while not crash:    
            if self.online:
                self.SendOnline()
                #print("online")
            time.sleep(1)

    # Отправка онлайн метки
    def SendOnline(self):      
        # Формируем сообщение
        onlineMsg = can.Message(arbitration_id = 0x600, extended_id = False, data = []) 
        self.Bus.send(onlineMsg)

    # Запуск потока отправки онлайнов
    def StartSendOnline(self):
        OnlineThread = threading.Thread(target = self.SendOnlineThread)
        OnlineThread.start()
        self.StartSendOnline = self.ZeroFunction                

    # Остановка потока отправки онлайнов    
    def StopSendOnline(self):
        self.online = False
        self.StartSendOnline = Robot.StartSendOnline   

    # Проверка наличия устройств, включенные устройства отвечают на команду, посылаемую этой функцией
    def DeviceRequest(self):
        self.answeredDeviceList.clear()
        AskMsg = can.Message(arbitration_id = 0x500, extended_id = False, data = []) 
        self.Send(AskMsg)
        
    def AddDevice(self, device):
        self.deviceList.append(device)  # Добавляем в список устройств

    # Функция запускаемая в потоке. Отвечает за прием сообщений
    def PreThreadRecv(self):
        global crash

        self.queueRecvMsg = queue.LifoQueue()
        while not (crash or self.stopRecv):
            inMsg = self.Recv()                      # Получение сообщения
            self.queueRecvMsg.put(inMsg)
            
    # Функция запускаемая в потоке. Отвечает за обработку принятых сообщений
    def ThreadRecv(self):
        global crash

        while not (crash or self.stopRecv):

            if not self.queueRecvMsg.empty(): # Если список сообщений не пуст
                
                inMsg = self.queueRecvMsg.get()                      # Извлечение сообщения из списка

                if (inMsg.arbitration_id == 0x501) and (inMsg.dlc == 7):
                    answer = struct.Struct('=2H 3B').unpack(inMsg.data)
                    device = (answer[2], answer[0], answer[3], answer[4])
                    self.answeredDeviceList.append(device)
                    print('Device type:%d  CAN ID:%X  Soft version:%d.%d' %(answer[2], answer[0], answer[3], answer[4]))
                    

                for device in self.deviceList: # Пробегаемся по всем устройствам

                    if inMsg.arbitration_id == (device.CanAddr + 0xFF): # Если нам ответило устройство с адрессом равным адрессу устройства которое мы сейчас проверяем в цикле
                        prmNumber = inMsg.data[0]

                        if device.ParamExist(prmNumber):  # Существует ли параметр в списке параметров данного устройства
                            prmLengthRecv = inMsg.data[1]

                            #if inMsg.dlc == prmLengthRecv + 2:  # Два байта занято номером параметра и значением длины
                            if True:
                                if inMsg.dlc > prmLengthRecv + 2:
                                    inMsg.data = inMsg.data[0:(prmLengthRecv + 2)]
                                prmStruct, prmLength = device.GetStructParam(device.GetParam(inMsg.data[0], 1))   # Выявление структуры и длины для данного типа сообщения

                                if prmLength == prmLengthRecv:  # Длина принятого параметра соответствует длине параметра в парам листе 
                                    unpackedPrm = prmStruct.unpack(inMsg.data)
                                    device.SetParam(prmNumber, unpackedPrm[2])  # Пробуем записать полученное значение параметра в список параметров

                                    if (prmNumber == 0x00) and (device.GetParam(0x00) == MagicNumber) and (device.isConnected == False): # Проверка соединения
                                        device.__isConnected = True
                                        print('Device "%s" (CAN ID: %X) connected' % (device.ControllerName, device.CanAddr))

                                    # Обработчик событий

                                    if device.BasicOnGetParam != None:
                                        device.BasicOnGetParam(prmNumber, device.GetParam(prmNumber))

                                    #print('Param recieved. Name:%s  Value:%s' % (self.ParamList[prmNumber][0], str(self.ParamList[prmNumber][2])))
                                else:
                                    print('Recieved length not according with recieving type')
                            else:
                                print('Recieved dlc not according with data length')
                        else:
                            print('Попытка принять неизвестный параметр:%d' % prmNumber)
            else:
                time.sleep(0.1) # Если список сообщений пуст, ждем 

    # Функция запускающая поток прослушивания кэн 
    def StartRecv(self):
        self.stopRecv = False
        PreRecvThread = threading.Thread(target = self.PreThreadRecv)
        PreRecvThread.start()
        time.sleep(0.1)
        RecvThread = threading.Thread(target = self.ThreadRecv)
        RecvThread.start()
        self.StartRecv = self.ZeroFunction                

    # Функция останавливающая поток прослушивания кэн
    def StopRecv(self):
        self.stopRecv = True
        self.StartRecv = Robot.StartRecv                
        
    # Для блокирования доступа к ф-ии будем присваивать ей значение пустой функции
    def ZeroFunction(self):
        pass
