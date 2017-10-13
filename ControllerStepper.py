from ControllerBase import *


# Контроллер шаговых двигателей

class ControllerStepper(ControllerBase):

    def __init__(self, owner = None, addr = 0):
        # canId = 230, есть селектор на 9 адрессов
        try:
            # Возможные адреса лежат в диапазоне 0-8
            assert(0 <= addr < 9), ("ERROR adress controller")
            super().__init__(owner, 0x230 + addr, 'ControllerStepper')
        except:            
            global crash
            print("Crashed")
            crash = True
            sys.exit(1)
            
        self.BasicOnGetParam = self.BasicOnGetParamNew
        self.OnGetParam = None

        # Стандартные параметры доступных длин осей в шагах шагового двигателя

        self.calibrateRange = [4496, 2915, 1216] # Для оранжевой головы риты

        # Дополняем словарь команд
        self.__CommandList = self._ControllerBase__CommandList.update({
                        # Команды управления
                  # name, type, length       

            0xCC:['Set work mode', DT_UINT8, DT_UINT8], # Номер мотора, режим работы
            0xCD:['Set velocity', DT_UINT8, DT_INT16],  # Номер мотора, скорость
            0xCE:['Robot drive', DT_UINT16, DT_UINT16], # Скорость, угол
            0xCF:['Set position', DT_UINT8, DT_UINT16], # Номер мотора, позиция
            0xD0:['Calibration', DT_UINT8, DT_UINT8],   # Номер мотора, тип калибровки
            0xD1:['Set all position', DT_UINT16, DT_UINT16, DT_UINT16], # Три позиции
                        })

        # Дополняем словарь параметров
        self.__ParamList = self._ControllerBase__ParamList.update({
                # Параметры для чтения и записи
            # name, type, (data)

            # Первый ШД
            0x01:['Debug info mask', DT_UINT8],
            0x02:['Calibrate step length', DT_UINT16],  #
            0x03:['Min step length', DT_INT16],
            0x04:['Max step length', DT_INT16],
            0x05:['Accel brake step', DT_UINT16],

            0x06:['Motor state', DT_UINT8],             #
            0x07:['Motor mode', DT_UINT8],              #
            0x08:['Set velocity', DT_INT16],
            0x09:['Current velocity', DT_INT16],
            
            0x0A:['Set position', DT_UINT16],
            0x0B:['Current position', DT_INT16],
            0x0C:['Motor calibrate state', DT_UINT8],   #
            0x0D:['Calibrate range', DT_UINT16],        #

            # Второй ШД
            0x0E:['Debug info mask', DT_UINT8],
            0x0F:['Calibrate step length', DT_UINT16],
            0x10:['Min step length', DT_INT16],
            0x11:['Max step length', DT_INT16],
            0x12:['Accel brake step', DT_UINT16],

            0x13:['Motor state', DT_UINT8],
            0x14:['Motor mode', DT_UINT8],
            0x15:['Set velocity', DT_INT16],
            0x16:['Current velocity', DT_INT16],
            
            0x17:['Set position', DT_UINT16],
            0x18:['Current position', DT_INT16],
            0x19:['Motor calibrate state', DT_UINT8],
            0x1A:['Calibrate range', DT_UINT16],
                       
            # Третий ШД
            0x1B:['Debug info mask', DT_UINT8],
            0x1C:['Calibrate step length', DT_UINT16],
            0x1D:['Min step length', DT_INT16],
            0x1E:['Max step length', DT_INT16],
            0x1F:['Accel brake step', DT_UINT16],

            0x20:['Motor state', DT_UINT8],
            0x21:['Motor mode', DT_UINT8],
            0x22:['Set velocity', DT_INT16],
            0x23:['Current velocity', DT_INT16],
            
            0x24:['Set position', DT_UINT16],
            0x25:['Current position', DT_INT16],
            0x26:['Motor calibrate state', DT_UINT8],
            0x27:['Calibrate range', DT_UINT16],
                        })

            
    def SetWorkMode(self, workMode):
        self.SetWorkModeSingle(0, workMode)
        self.SetWorkModeSingle(1, workMode)
        self.SetWorkModeSingle(2, workMode)        
        
    def SetWorkModeSingle(self, stepperN, workMode):    # 2 - позиционирование(с концевиками)  1 - свободное вращение (без концевиков)
        self.SendCommand(0xCC, (stepperN, workMode))

    def SetVelocity(self, stepperN, velocity):
        self.SendCommand(0xCD, (stepperN, velocity))

    def RobotDrive(self, velocity, angle): # Для робота на шаре
        self.SendCommand(0xCE, (velocity, angle))

    def Calibrate(self, stepperN, calibType = 1): # 0 - полная калибровка, 1 - быстрая калибровка.
        self.SendCommand(0xD0, (stepperN, calibType))

    def SetPosition(self, stepperN, position):
        # Задание углов
        angles = [270, 210, 140]

        # Установка предельных значений углов
        limits = [130, 100, 85]

        # Обработка заданной в углах позиции
        if abs(position)>limits[stepperN]:
            position = limits[stepperN]*(position//abs(position))

        # Преобразование углов в количество шагов
     
        position = int((self.calibrateRange[stepperN]/angles[stepperN])*(angles[stepperN]//2 + position))
        print(position)

        self.SendCommand(0xCF, (stepperN, position))
        

    def SetAllPositions(self, position0, position1, position2): # Позиции задаются в углах. От -135 до 135, от -105 до 105, от -90 до 90

        # Обработка позиций
        # Установка предельных значений углов

        limits = [130, 100, 85]
        
        if abs(position0)>limits[0]:
            position0 = limits[0]*(position0//abs(position0))

        if abs(position1)>limits[1]:
            position1 = limits[1]*(position1//abs(position1))

        if abs(position2)>limits[2]:
            position2 = limits[2]*(position2//abs(position2))

        # Преобразование углов в количество шагов
        
        position0 = (self.calibrateRange[0]//270)*(135 + position0)
        position1 = (self.calibrateRange[1]//210)*(105 + position1)
        position2 = (self.calibrateRange[2]//180)*(90 + position2)

        self.SendCommand(0xD1, (position0, position2, position1)) # Позиции в прошивке этой команды перепутаны, в ней моторы нумеруются 0,2,1

    # Функция, вызываемая при приеме параметра
    def BasicOnGetParamNew(self, prmNumber, prm):
        super().BasicOnGetParam(prmNumber, prm) # Функция вызываемая при приеме параметра, описанная в модуле ControllerBase 
        if self.OnGetParam != None:
            self.OnGetParam(prmNumber, prm)

        # При приеме сообщения после калибровки (количество доступных шагов по трём осям)
        for i in range (3):
            if prmNumber == 0x0D+i*13:
                self.calibrateRange[i] = prm
                print('Calibrate steps: ', self.calibrateRange)
