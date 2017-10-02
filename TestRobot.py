from Robot import*
import RTCvrangle                                                                                 
#import time                                                                                       
n = 0                                                                                                  
angle=[]                                                                                          
oldAngle = [0,0,0]

def ARBUZIUS(prmNumber, prm):
    print('prmNumber:%s  param:%d' % (hex(prmNumber), prm))

Marvin = Robot('can0')

CS = ControllerStepper(Marvin)
CS.onGetParam = ARBUZIUS

Marvin.online = True

#CS.SetWorkMode(2)
#CS.Calibrate(0,0)

def handler(ang):                                                                                 
    global angle, oldAngle, n
    n += 1
    angle=ang                                                                                     
    print('yaw:%d pitch:%d roll:%d' % (int(angle[0]), int(angle[1]), int(angle[2])))                                                                                  
    for number in range(2):
        if abs(oldAngle[number]-angle[number])>2:
            CS.SetAllPositions(-int(angle[0]), -int(angle[2]), int(angle[1])) 
            oldAngle[number] = angle[number]
def handler1():                                                                                   
    print("\nI stoped\n")                                                                         
                                                                                                  
def handler2():                                                                                   
    print("\nI started\n")                                                                        
                                                                                                  

# ОЧКИ

VR_TH=RTCvrangle.VR_thread("/dev/ttyUSB0")                                                        
VR_TH.start()                                                                                     
                                                                                                  
VR_TH.connect("START", handler2)                                                                  
VR_TH.connect("STOP", handler1)                                                                   
VR_TH.connect("READ", handler)                                                                    

time.sleep(100)

VR_TH.Exit()                                                                                      #####


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

#time.sleep(2)
#CS.SetWorkMode(2)

#CS.SetAllPositions(2245,606,1450) # Стартер поз
#CS.SetAllPositions(-90,-90,-90) # Стартер поз
# Необходимо перед заданием позиций узнавать количество доступных шагов по каждой оси. После этого можно сохранять эти шкалы и относительно них задавать позиции.
#CS.SetPosition(1,0)
#CS.SetPosition(2,45)
#CS.Calibrate(0,0)
#CS.Calibrate(1,0)
#CS.Calibrate(2,0)

#CS.SetVelocity(0, 10)
#CS.SendCommand(0xCA) # ЗАПИСЬ В ЕПРОМ
#time.sleep(8)

#CS.SetWorkMode(0)

#Marvin.DeviceRequest()
#time.sleep(2)
#print(Marvin.answeredDeviceList)

#time.sleep(5)

