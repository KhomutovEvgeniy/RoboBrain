from RoboMind import *

def ARBUZIUS(prmNumber, prm):
    print('prmNumber:%d  param:%d' % (prmNumber, prm))

C = ControllerMotor()
C.onGetParam = ARBUZIUS
#C.SetWorkMode(1)
O = Onliner()
O.online = True
time.sleep(4)
#C.SetSpeed(0, 50)
