from Robot import*

def ARBUZIUS(prmNumber, prm):
    print('prmNumber:%s  param:%d' % (hex(prmNumber), prm))

Marvin = Robot('can0')

CS = ControllerStepper(Marvin)
CS.onGetParam = ARBUZIUS

Marvin.online = True

#CS.SendParam(0x02, 100)
#CS.SendParam(0x0F, 100)
#CS.SendParam(0x1C, 100)
#CS.SendParam(0x03, 20)
#CS.SendParam(0x04, 50)
'''CS.SendParam(0x05, 2)

CS.SendParam(0x10, 20)
CS.SendParam(0x11, 60)
CS.SendParam(0x12, 2)

CS.SendParam(0x1D, 20)
CS.SendParam(0x1E, 60)
CS.SendParam(0x1F, 2)'''


#CS.SendCommand(0xC9)

time.sleep(2)
#CS.SetWorkMode(2)

#CS.SetAllPositions(2245,606,1450) # Стартер поз
#CS.SetAllPositions(-90,-90,-90) # Стартер поз
# Необходимо перед заданием позиций узнавать количество доступных шагов по каждой оси. После этого можно сохранять эти шкалы и относительно них задавать позиции.
CS.SetPosition(1,0)
#CS.Calibrate(0,0)
#CS.Calibrate(1,0)
#CS.Calibrate(2,0)

#CS.SetVelocity(0, 10)
#CS.SendCommand(0xCA) # ЗАПИСЬ В ЕПРОМ
time.sleep(8)

#CS.SetWorkMode(0)

#Marvin.DeviceRequest()
time.sleep(2)
#print(Marvin.answeredDeviceList)

time.sleep(5)
