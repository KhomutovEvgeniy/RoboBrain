### Описание параметров контроллеров в виде словарей
import can
import struct

def vacuum(self):
    pass

def MotorSpeedHandler(self):
    typeSpeed = struct.Struct('=2b h')              # Структура сообщения
    packedData = typeSpeed.pack(self.motorNumber+10, 2, self.speed)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    
    return packedMessage    # Возвращаем упакованное сообщение

def 2bh_Handler(self):
    typeSpeed = struct.Struct('=2b h')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber+10, 2, self.prm)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    
    return packedMessage    # Возвращаем упакованное сообщение


    
# ControllerMotor
ParamListMC = {'0xc8':{'help':'work mode', 'handler': None},
               '0xc9':{'help':'send parameters', 'handler': None},
               '0xca':{'help':'write in EEPROM', 'handler': None},
               '0xcb':{'help':'read from EEPROM', 'handler': None},
               '0xcc':{'help':'clear odometres', 'handler': None},
               '0xcd':{'help':'set PWM for same time', 'handler': None},
               '0xce':{'help':'set PWM', 'handler': None},
               '0xcf':{'help':'set speed', 'handler': MotorSpeedHandler},
               '0xd0':{'help':'set all PWM', 'handler': None},
               '0xd1':{'help':'set all speeds', 'handler': None},
               '0xd2':{'help':'power out', 'handler': None},
              }

# ControllerStepper
ParamListSC = {'1':{'help':'asdasdas', 'value':123}}

def Handlerissimo(self):

    if self.CanAddr == 0x200:
        return ParamListMC[hex(self.prmNumber)]['handler'](self)

    if self.CanAddr == 0x230:
        return ParamListSC[str(self.prmNumber)]['handler'](self)



## ВНИМАНИЕ
# Шестнадцатиричные числа в ключах необходимо записывать в нижнем регистре.
# Т.к. при переводе шестнадцатиричного числа в строку оно записывается в нижнем регистре.
