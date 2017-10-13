from ControllerBase import *

class ControllerServo(ControllerBase):    

    def __init__(self, owner = None, addr = 0x220):
        
        try:
            super().__init__(owner, addr, 'ControllerServo')      
        except:            
            global crash
            print("Crashed")
            crash = True
            sys.exit(1)

        # Информация по сервам. Текущая позиция, нулевая позиция. 
        self.ServoParam = ((None, None),
                           (None, None),
                           (None, None),
                           (None, None),
                           (None, None),
                           (None, None),
                           (None, None),
                           (None, None))

        # Дополняем словарь команд
        self.__CommandList = self._ControllerBase__CommandList.update({   
            # Команды управления
            # name, type
            0xCD:['set start pos'],
            0xCE:['set power out', DT_UINT8, DT_UINT8],
            0xCF:['set servo pos', DT_UINT8, DT_UINT8],
                       })

        # Дополняем словарь параметров
        self.__ParamList = self._ControllerBase__ParamList.update({
            # Параметры для чтения и записи
            # name, type, (data)
            0x01:['servo position 0', DT_UINT8, 0],
            0x02:['servo position 1', DT_UINT8, 0],
            0x03:['servo position 2', DT_UINT8, 0],
            0x04:['servo position 3', DT_UINT8, 0],
            0x05:['servo position 4', DT_UINT8, 0],
            0x06:['servo position 5', DT_UINT8, 0],
            0x07:['servo position 6', DT_UINT8, 0],
            0x08:['servo position 7', DT_UINT8, 0],
            0x09:['servo zero position 0', DT_UINT8],
            0x0A:['servo zero position 1', DT_UINT8],
            0x0B:['servo zero position 2', DT_UINT8],
            0x0C:['servo zero position 3', DT_UINT8],
            0x0D:['servo zero position 4', DT_UINT8],
            0x0E:['servo zero position 5', DT_UINT8],
            0x0F:['servo zero position 6', DT_UINT8],
            0x10:['servo zero position 7', DT_UINT8],
            0x11:['power out 0', DT_UINT8],
            0x12:['power out 1', DT_UINT8],
                      })

    def SetServoPos(self, servoNumber, position):
        if 0 <= servoNumber < 8:
            if position > 250:
                position = 250
            self.SendCommand(0xCF, (servoNumber, position))
        else:
            print('Uncorrect number of servo')

    def GetServoPos(self, servoNumber):
        return self.__ParamList[servoNumber][2]
        
    # Функция, вызываемая при приеме параметра    
    def BasicOnGetParamNew(self, prmNumber, prm):

        information = []
        
        for tuples in self.ServoParam:
            information.append(list(tuples))
                                                                                                                                                          
        for i in range(8):          # 8 - кол-во возможных серв
            if prmNumber == 0x01 + i:   # Позиция i-го серва
                information[i][0] = prm
            elif prmNumber == 0x09 + i: # Нулевая позиция i-го серва
                information[i][1] = prm

        servoParam = []
        
        for lists in information:
            servoParam.append(tuple(lists))

        self.ServoParam = tuple(servoParam)

        super().BasicOnGetParam(prmNumber, prm) # Функция вызываемая при приеме параметра, описанная в модуле ControllerBase 

    

    #def SetZeroPos()

    def SetPowerOut(self, powerOutNumber, state):
        if 0 <= powerOutNumber < 2:
            if state != 0:
                state = 1
            self.SendCommand(0xCE, (powerOutNumber, state))
        else:
            print('Uncorrect number of powerOut')
        
        
