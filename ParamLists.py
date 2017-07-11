### Описание параметров контроллеров в виде словарей, а так же функции упаковки сообщения в тип can message
import can
import struct

'''
def MotorSpeedHandler(self):
    typeSpeed = struct.Struct('=2b h')              # Структура сообщения
    packedData = typeSpeed.pack(self.motorNumber+10, 2, self.speed)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    return packedMessage    # Возвращаем упакованное сообщение
'''

def Int16Handler(self):
    typeSpeed = struct.Struct('=2b h')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber, 2, self.data)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    return packedMessage    # Возвращаем упакованное сообщение

def UInt16Handler(self):
    typeSpeed = struct.Struct('=2b H')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber, 2, self.data)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    return packedMessage    # Возвращаем упакованное сообщение

def UInt8Handler(self):
    typeSpeed = struct.Struct('=2b B')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber, 1, self.data)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    return packedMessage    # Возвращаем упакованное сообщение

def Int32Handler(self):
    typeSpeed = struct.Struct('=2b l')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber, 4, self.data)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    
    return packedMessage    # Возвращаем упакованное сообщение

def FloatHandler(self):
    typeSpeed = struct.Struct('=2b f')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber, 4, self.data)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    
    return packedMessage    # Возвращаем упакованное сообщение

def ByteHandler(self):
    typeSpeed = struct.Struct('=2b B')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber, 1, self.data)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    
    return packedMessage    # Возвращаем упакованное сообщение

def NoneHandler(self):
    typeSpeed = struct.Struct('=2b')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber, 0)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    
    return packedMessage    # Возвращаем упакованное сообщение

def ByteShortHandler(self):
    typeSpeed = struct.Struct('=2b B h')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber, 3, self.prm, self.prm2)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    
    return packedMessage    # Возвращаем упакованное сообщение

)

def ShortShortHandler(self):
    typeSpeed = struct.Struct('=2b h h')              # Структура сообщения
    packedData = typeSpeed.pack(self.prmNumber, 4, self.prm, self.prm2)  # Упаковываем сообщение

    # extended_id - фолс - 11 бит, тру - 29
    packedMessage = can.Message(arbitration_id = self.CanAddr,
                                extended_id = False,       
                                data = packedData)
    
    return packedMessage    # Возвращаем упакованное сообщение

)


    
# ControllerMotor
ParamListMC = {
                        # Команды управления

               '0xc8':{'name':'work mode', 'type': 'UInt8'}, # пример
               '0xc9':{'help':'send parameters', 'handler': NoneHandler},
               '0xca':{'help':'write in EEPROM', 'handler': NoneHandler},
               '0xcb':{'help':'read from EEPROM', 'handler': NoneHandler},
               '0xcc':{'help':'clear odometres', 'handler': NoneHandler},
               '0xcd':{'help':'set PWM for same time', 'handler': None},    # Не известно
               '0xce':{'help':'set PWM', 'handler': UInt8Int16Handler},
               '0xcf':{'help':'set speed', 'handler': UInt8Int16Handler},
               '0xd0':{'help':'set all PWM', 'handler': Int16Int16Handler},
               '0xd1':{'help':'set all speeds', 'handler': Int16Int16Handler},
               '0xd2':{'help':'power out', 'handler': UInt8Handler},

                        # Параметры для чтения и записи 

               '0x00':{'help':'debug info mask', 'handler': UInt8Handler},
               '0x01':{'help':'proportional coefficient', 'handler': FloatHandler},
               '0x02':{'help':'integral coefficient', 'handler': FloatHandler},
               '0x03':{'help':'derivative coefficient', 'handler': FloatHandler},
               '0x04':{'help':'limit summ', 'handler': Int16Handler},
               '0x05':{'help':'time PID', 'handler': UInt16Handler},
               '0x06':{'help':'time PWM', 'handler': UInt16Handler},
               '0x07':{'help':'pwm DeadZone', 'handler': UInt8Handler},
               '0x08':{'help':'accelbreak step', 'handler': UInt8Handler},
               '0x09':{'help':'emergency level', 'handler': UInt16Handler},

                       # Параметры только для чтения

               '0x13':{'help':'Error Code', 'handler': UInt8Handler},
               '0x14':{'help':'Work mode', 'handler': UInt8Handler},

               # 1 
               
               '0x15':{'help':'pParrot1', 'handler': FloatHandler},
               '0x16':{'help':'iParrot1', 'handler': FloatHandler},
               '0x17':{'help':'dParrot1', 'handler': FloatHandler},
               '0x18':{'help':'res PWM1', 'handler': Int16Handler},
               '0x19':{'help':'current Parrot1', 'handler': Int16Handler},
               '0x1a':{'help':'encoder Data1', 'handler': Int32Handler},
               '0x1b':{'help':'Int summ1', 'handler': Int16Handler},
               '0x1c':{'help':'adc Average1', 'handler': UInt16Handler},
               '0x1d':{'help':'set Parrot1', 'handler': Int16Handler},
               '0x1e':{'help':'set PWM1', 'handler': Int16Handler},

               # 2 
               
               '0x1f':{'help':'pParrot2', 'handler': FloatHandler},
               '0x20':{'help':'iParrot2', 'handler': FloatHandler},
               '0x21':{'help':'dParrot2', 'handler': FloatHandler},
               '0x22':{'help':'res PWM2', 'handler': Int16Handler},
               '0x23':{'help':'current Parrot2', 'handler': Int16Handler},
               '0x24':{'help':'encoder Data2', 'handler': Int32Handler},
               '0x25':{'help':'Int summ2', 'handler': Int16Handler},
               '0x26':{'help':'adc Average2', 'handler': UInt16Handler},
               '0x27':{'help':'set Parrot2', 'handler': Int16Handler},
               '0x28':{'help':'set PWM2', 'handler': Int16Handler},
               
              }

# ControllerStepper
ParamListSC = {'1':{'help':'asdasdas', 'value':123}}


## ВНИМАНИЕ
# Шестнадцатиричные числа в ключах необходимо записывать в нижнем регистре.
# Т.к. при переводе шестнадцатиричного числа в строку оно записывается в нижнем регистре.
