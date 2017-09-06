from ControllerMotor import *
from ControllerServo import *
from ControllerBase import *


def ARBUZIUS(prmNumber, prm):
    print('prmNumber:%d  param:%d' % (prmNumber, prm))


C = ControllerMotor()
C.onGetParam = ARBUZIUS
time.sleep(0.1)
assert C.isConnected, 'ERROR controller motor connection'
S = ControllerServo()
S.onGetParam = ARBUZIUS
time.sleep(0.1)
assert S.isConnected, 'ERROR controller servo connection'

O = Onliner()
O.online = True
time.sleep(2)


S.SetPowerOut(0, 1)
S.SetPowerOut(1, 1)

#C.SetWorkMode(1)
time.sleep(2)

S.SetPowerOut(0, 0)
S.SetPowerOut(1, 0)

#C.SetSpeed(0, 50)
IAH = IsAnybodyHere()
if IAH.DeviceRequest():
    print(IAH.deviceList)
print(S.ServoPos)    
time.sleep(10)
