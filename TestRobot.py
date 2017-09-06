from Robot import*

def ARBUZIUS(prmNumber, prm):
    print('prmNumber:%d  param:%d' % (prmNumber, prm))

Marvin = Robot('can0')

CS = ControllerStepper(Marvin)
CS.onGetParam = ARBUZIUS

Marvin.online = True

CS.SendCommand(0xC9)
#CS.SetWorkMode(2)

#CS.Calibrate(0,0)
#CS.Calibrate(1,0)
#CS.Calibrate(2,0)

#CS.SetVelocity(0, 10)

time.sleep(4)

#CS.SetWorkMode(0)

Marvin.DeviceRequest()
time.sleep(2)
#print(Marvin.answeredDeviceList)

time.sleep(5)
