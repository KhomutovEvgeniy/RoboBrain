from Robot import*
def ARBUZIUS(prmNumber, prm):
    print('prmNumber:%s  param:%d' % (hex(prmNumber), prm))

Marvin = Robot('can0')

CM1 = ControllerMotor(Marvin)
CM1.onGetParam = ARBUZIUS
time.sleep(300)
'''
Marvin.online = True

CM1.SetWorkMode(2)
CM1.SetMotorPWM(0, -180)
CM1.SetMotorPWM(1, -180)

#CM1.SetSpeed(0, -50)
#CM1.SetSpeed(1, -50)
time.sleep(5)

CM1.SetMotorPWM(0, 255)
CM1.SetMotorPWM(1, 255)
#CM1.SetSpeed(0, 100)
#CM1.SetSpeed(1, 100)
time.sleep(5)
CM1.SetMotorPWM(0, 0)
CM1.SetMotorPWM(1, 0)
#CM1.SetSpeed(0, 0)
#CM1.SetSpeed(1, 0)
time.sleep(5)
CM1.SetMotorPWM(0, -180)
CM1.SetMotorPWM(1, -180)
#CM1.SetSpeed(0, -50)
#CM1.SetSpeed(1, -50)
time.sleep(5)
CM1.SetMotorPWM(0,0)
CM1.SetMotorPWM(1,0)
#CM1.SetSpeed(0, 0)
#M1.SetSpeed(1, 0)
#CM.SetWorkMode(0)
'''
