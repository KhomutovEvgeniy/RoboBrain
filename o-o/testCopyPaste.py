##### Пример программы, использующей эти классы:                                                        #####
                                                                                                  #####
import RTCvrangle                                                                                 #####
import time                                                                                       #####
                                                                                                  #####
angle=[]                                                                                          #####
                                                                                                  #####
def handler(ang):                                                                                 #####
    global angle                                                                                  #####
    angle=ang                                                                                     #####
    print('yaw:%d pitch:%d roll:%d' % (int(angle[0]), int(angle[1]), int(angle[2])))                                                                                  #####
                                                                                                  #####
def handler1():                                                                                   #####
    print("\nI stoped\n")                                                                         #####
                                                                                                  #####
def handler2():                                                                                   #####
    print("\nI started\n")                                                                        #####
                                                                                                  #####
VR_TH=RTCvrangle.VR_thread("/dev/ttyUSB0")                                                        #####
VR_TH.start()                                                                                     #####
                                                                                                  #####
VR_TH.connect("START", handler2)                                                                  #####
VR_TH.connect("STOP", handler1)                                                                   #####
VR_TH.connect("READ", handler)                                                                    #####
                                                                                                  #####
time.sleep(400)                                                                                    #####
VR_TH.Exit()                                                                                      #####
    
