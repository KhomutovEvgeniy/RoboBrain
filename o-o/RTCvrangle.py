###########################################################################################################
##### class VR_Angle - чтение и обработка приходящих из VR очков сообщений, преобразование их в углы. #####
##### class VR_Thread - запуск чтения и обработки сообщений с очков в отдельном потоке, а также класс #####
##### имеет встроенные функции, позволяющие за пределами потока затребовать углы и выйти из потока    #####
###########################################################################################################


import serial
import threading
import time
import RTCevent_master

class VR_Angle():                                                               
        def __init__(self, portname, yaw=0,  pitch=0, roll=0):          #конструктор
            self.port = serial.Serial(portname, baudrate=115200)        #открытие порта
            self.yaw = yaw                                              #                                        
            self.pitch = pitch                                          # углы поворота
            self.roll = roll                                            #
            
            self.yaw0 = yaw                                             #
            self.pitch0 = pitch                                         # нулевые углы, задаются кнопками старт/стоп на очках 
            self.roll0 = roll                                           #
            
            self.buff=b''                                               # буффер для строки, прилетевшей с очков
            self.listbuff=[]                                            # предыдущая строка, в которой слова разделены пробелами
            self.startflag=False                                        # флаг нажатия кнопки старт, для последующего выбора нулевых углов
            self.PLAYING=False                                          # флаг режима чтения углов
            self.exit=False                                             # метка выхода из цикла

        ################## Список событий  ############################
            self.EVENT_LIST=[RTCevent_master.Event_block("START"), RTCevent_master.Event_block("STOP"), RTCevent_master.Event_block("EXIT"), RTCevent_master.Event_block("READ")]        
 
        ###########################################################################################


        def __del__(self):                                                # деструктор
            self.port.close()                                           # закрытие порта

        def read_bytesstr(self):                                        # чтение строки,заключенной между < >, с очков и запись ее в буффер
            k=self.port.read()
            while k!=b'<':
                k=self.port.read()
            while k!=b'>':
                if k!=b'<':
                    self.buff+=k
                k=self.port.read()
                

        def convert_srtbuffer(self):                                    # сортировка сообщений с очков и перевод углов
            self.listbuff = list(map(bytes, self.buff.split()))         # разделение сообщения на слова и запись их в список

            if self.listbuff[0]==b'ypr':                                # если первое слово ypr
                self.yaw = float(self.listbuff[1])                      # 
                self.pitch = float(self.listbuff[2])                    # преобразование байтовых слов в float
                self.roll = float(self.listbuff[-1])                    #
                

            if(self.startflag):                                         # если была нажата кнопка start
                self.yaw0 = self.yaw                                    #  
                self.pitch0 = self.pitch                                # текущие углы сделать нулевыми
                self.roll0 = self.roll                                  #
                self.startflag=False                                    # убрать флаг нажатия кнопки старт
            
                
            if self.listbuff[0]==b'*':                                  # если сообщение начинается с *
                print("\n COMMENT: ")                                   # вывод комментария
                print(str(self.buff))                                   #

            if self.listbuff[0]==b'start':                              # если пришло сообщение start(была нажата кнопка start)
                self.EVENT_LIST[0].push()                               # вызвать событие нажатия кнопки старт
                self.startflag = True                                   # поставить флаг нажатия кнопки старт
                self.PLAYING=True                                       # поставить флаг режима чтения углов
                
                
            if self.listbuff[0]==b'stop':                               # если пришло сообщение stop(была нажата кнопка stop)                                
                self.yaw0 = 0                                           #  
                self.pitch0 = 0                                         # сбросить текущие углы
                self.roll0 = 0                                          #
                self.EVENT_LIST[1].push()                               # вызвать событие нажатия кнопки стоп
                self.PLAYING=False                                      # снять флаг режима чтения углов

            if(self.PLAYING):                                           # если включен режим чтения углов
                self.EVENT_LIST[3].push()                               # вызвать событие чтения углов

            


        def VR_EXIT(self):                                              # функция закрывающая поток
            self.exit=True                                              # поставить метку выхода из цикла
            self.EVENT_LIST[2].push()                                   # вызвать событие чтения углов
            
        def get_yaw(self):                                              # доступ к yaw
            return self.yaw-self.yaw0
        
        def get_pitch(self):                                            # доступ к pitch
            return self.pitch-self.pitch0
        
        def get_roll(self):                                             # доступ к roll
            return self.roll-self.roll0
        
        def get_ypr_list(self):                                         # доступ к списку координат
            A=[self.yaw-self.yaw0, self.pitch-self.pitch0, self.roll-self.roll0]
            return A

     

        def start_read_VR_angle(self):                                  # начать чтение с очков
            self.read_bytesstr()                                        
            self.buff=b''
            time.sleep(2)
            self.port.write(b'g')                                       # для того, чтоб очки начали передавать координаты, необходимо отправить символ на них 
            while not self.exit:                                        # выход из цикла           
                self.read_bytesstr()                    
                self.convert_srtbuffer()
                self.buff=b''


class VR_thread(threading.Thread):                                      # потоковый класс
    def __init__(self, Portname):                                       # конструктор
        threading.Thread.__init__(self)                                 # функция инициализирующая поток
        self.portname=Portname
        self.VR = VR_Angle(self.portname)                               # создание объекта класса VR_Angle
        self.EV=RTCevent_master.EVENT_MASTER()                             # создание объекта класса EVENT_MASTER
        self.EV.start()                                                 # запуск EV в отдельном потоке

    def run(self):                                                      # функция запуска потока       
        self.VR.start_read_VR_angle()                                   # циклится, пока не придет метка закрытия потока
        print("VR_THREAD stopped\n")


    def Exit(self):                                                     # функция выхода их потока за пределами потока
        self.VR.VR_EXIT()                                               # выход из цикла в VR
        self.EV.exit()                                                  # выход из потока в EV
        del self.VR

    def get_angle(self):                                                # функция доступа к углам за пределами потока
        return self.VR.get_ypr_list()

    def connect(self, Name, funct):                                     # функция привязывающая функции пользователя к определенным событиям
        connected=False                                                 # метка подключения функции к событию
        for event in self.VR.EVENT_LIST:                                # цикл по каждому событию в EVENT_LIST
            if(Name==event.name):                                       # если имя события и заданное имя совпадает
                if(Name=="READ"):
                        
                    def READFun():                                      # EVENT_MASTER работает только с функциями с пустыми параметрами, для того, чтобы поместить функцию с параметрами в E_M 
                        funct(self.VR.get_ypr_list())                   # записываем ее, с необходимыми параметрами, в тело функции с пустыми параметрами 
                        
                    event.setFun(READFun)                               # событию присвоить функцию
                    self.EV.append(event)                               # добавить событие, с привязанной функцией, в EV
                    connected=True                                      # установить метку подключения
                else:
                    event.setFun(funct)                                 # событию присвоить функцию
                    self.EV.append(event)                               # добавить событие, с привязанной функцией, в EV
                    connected=True                                      # установить метку подключения
                    break
        if(connected):                                                  # если подключение успешно
            return 0
        else:                                                           # если нет
            print("Connected fail\n")
            return -1
                    




#############################################################################################################
#############################################################################################################
##### Пример программы, использующей эти классы:                                                        #####
#####                                                                                                   #####
##### import RTCvrangle                                                                                 #####
##### import time                                                                                       #####
#####                                                                                                   #####
##### angle=[]                                                                                          #####
#####                                                                                                   #####
##### def handler(ang):                                                                                 #####
#####     global angle                                                                                  #####
#####     angle=ang                                                                                     #####
#####     print(angle)                                                                                  #####
#####                                                                                                   #####
##### def handler1():                                                                                   #####
#####     print("\nI stoped\n")                                                                         #####
#####                                                                                                   #####
##### def handler2():                                                                                   #####
#####     print("\nI started\n")                                                                        #####
#####                                                                                                   #####
##### VR_TH=RTCvrangle.VR_thread("/dev/ttyUSB0")                                                        #####
##### VR_TH.start()                                                                                     #####
#####                                                                                                   #####
##### VR_TH.connect("START", handler2)                                                                  #####
##### VR_TH.connect("STOP", handler1)                                                                   #####
##### VR_TH.connect("READ", handler)                                                                    #####
#####                                                                                                   #####
##### time.sleep(40)                                                                                    #####
##### VR_TH.Exit()                                                                                      #####
#####                                                                                                   #####        
#############################################################################################################
#############################################################################################################
