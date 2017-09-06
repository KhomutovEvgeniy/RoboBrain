from ControllerBase import *


# Контроллер моторов

class ControllerMotor(ControllerBase):    

    def __init__(self, owner = None, addr = 0):

        try:
            # Возможные адреса лежат в диапазоне 0-8
            assert(0 <= addr < 9), ("ERROR adress controller")
            super().__init__(owner, 0x200 + addr, 'ControllerMotor')
        except:            
            global crash
            print("Crashed")
            crash = True
            sys.exit(1)

        # Информация по моторам. Номер мотора, скорость в попугаях, значения одометра, п, и ,д коэффициенты.
        self.MotorParam = ((None, None, None, None, None, None, None),
                            (None, None, None, None, None, None, None)) # Кортеж кортежей, содержащих информацию о двух моторах. Значение скорости, значение одометра, п, и, д коэффициенты, результирующий ШИМ, интегр сумма

        # Обработчики
        self.BasicOnGetParam = self.BasicOnGetParamNew
        self.OnOdometryChanged = None
        self.OnSpeedChanged = None

        
        # Дополняем словарь команд
        self.__CommandList = self._ControllerBase__CommandList.update({   
                        # Команды управления
                  # name, type, length
            0xCC:['work mode', DT_UINT8], # пример. Переделать в списки. Название - тип. Параметр задавать не текстом, а номером.
            0xCD:['clear odometres'],
            0xCE:['PWM pulse'],    # Не известно
            0xCF:['set PWM', DT_UINT8, DT_INT16],
            0xD0:['set speed', DT_UINT8, DT_INT16],
            0xD1:['set all PWM', DT_INT16, DT_INT16],
            0xD2:['set all speed', DT_INT16, DT_INT16],
            0xD3:['power out', DT_UINT8, DT_UINT8]

                       })

        # Дополняем словарь параметров
        self.__ParamList = self._ControllerBase__ParamList.update({
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

    def SetDebugInfoMask(self, tahometr = 1, odometr = 1, firstMotorData = 0, secondMotorData = 0, electricCurrent = 0):
        dimValue = tahometr*128 + odometr*64 + firstMotorData*32 + secondMotorData*16 + electricCurrent*8
        self.SendParam(0x01, dimValue)

    def SetWorkMode(self, workMode = 0):        # Инициализация режима работы (2 - ШИМ, 1 - включить ручной режим, 0 - пока используется как выключение ручного режима)
        self.SendCommand(0xCC, (workMode,))
        
    def SetAllSpeed(self, speed1, speed2): # Установить скорость мотора (0 и 1)
        self.SendCommand(0xD2, (speed1, speed2))

    def SetSpeed(self, motorNumber, speed): # Установить скорость мотора (0 и 1)
        self.SendCommand(0xD0, (motorNumber, speed))

    # Функция, вызываемая при приеме параметра    
    def BasicOnGetParamNew(self, prmNumber, prm):

        information = (list(self.MotorParam[0]), list(self.MotorParam[1]))

        ParamsAmount = 10

        for i in range(2):
            if prmNumber == 0x15 + i*ParamsAmount: # Пропорцинальный
                information[i][2] = prm
            elif prmNumber == 0x16 + i*ParamsAmount: # Интегральный
                information[i][3] = prm
            elif prmNumber == 0x17 + i*ParamsAmount: # Дифференциальный
                information[i][4] = prm
            elif prmNumber == 0x19 + i*ParamsAmount: # Скорость
                information[i][0] = prm
                if self.OnSpeedChanged != None:
                    self.OnSpeedChanged(i, prm)
            elif prmNumber == 0x1A + i*ParamsAmount: # Одометрия
                information[i][1] = prm
                if self.OnOdometryChanged != None:
                    self.OnOdometryChanged(i, prm)
            elif prmNumber == 0x18 + i*ParamsAmount: # Результирующий ШИМ
                information[i][5] = prm
            elif prmNumber == 0x1B + i*ParamsAmount: # Интегр Сумма
                information[i][6] = prm

        self.MotorParam = (tuple(information[0]), tuple(information[1]))

        super().BasicOnGetParam(prmNumber, prm) # Функция вызываемая при приеме параметра, описанная в модуле ControllerBase 


################## КАК ЗАДАВАТЬ ШИМ? ############
    def SetMotorPWM(self, motorNumber, PWM): 
        pass
#################################################
