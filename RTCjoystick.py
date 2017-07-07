import os, struct, array
import time
from fcntl import ioctl
import threading

axis_names = {
    0x00 : 'x',
    0x01 : 'y',
    0x02 : 'z',
    0x03 : 'rx',
    0x04 : 'ry',
    0x05 : 'rz',
    0x06 : 'trottle',
    0x07 : 'rudder',
    0x08 : 'wheel',
    0x09 : 'gas',
    0x0a : 'brake',
    0x10 : 'hat0x',
    0x11 : 'hat0y',
    0x12 : 'hat1x',
    0x13 : 'hat1y',
    0x14 : 'hat2x',
    0x15 : 'hat2y',
    0x16 : 'hat3x',
    0x17 : 'hat3y',
    0x18 : 'pressure',
    0x19 : 'distance',
    0x1a : 'tilt_x',
    0x1b : 'tilt_y',
    0x1c : 'tool_width',
    0x20 : 'volume',
    0x28 : 'misc',
}

button_names = {
    0x120 : 'trigger',
    0x121 : 'thumb',
    0x122 : 'thumb2',
    0x123 : 'top',
    0x124 : 'top2',
    0x125 : 'pinkie',
    0x126 : 'base',
    0x127 : 'base2',
    0x128 : 'base3',
    0x129 : 'base4',
    0x12a : 'base5',
    0x12b : 'base6',
    0x12f : 'dead',
    0x130 : 'a',
    0x131 : 'b',
    0x132 : 'c',
    0x133 : 'x',
    0x134 : 'y',
    0x135 : 'z',
    0x136 : 'tl',
    0x137 : 'tr',
    0x138 : 'tl2',
    0x139 : 'tr2',
    0x13a : 'select',
    0x13b : 'start',
    0x13c : 'mode',
    0x13d : 'thumbl',
    0x13e : 'thumbr',

    0x220 : 'dpad_up',
    0x221 : 'dpad_down',
    0x222 : 'dpad_left',
    0x223 : 'dpad_right',

    # XBox 360 controller uses these codes.
    0x2c0 : 'dpad_left',
    0x2c1 : 'dpad_right',
    0x2c2 : 'dpad_up',
    0x2c3 : 'dpad_down',
}

class Joystick():
    def __init__(self):
        self.path=None
        self.axis_map = []
        self.button_map = []
        self.jsdev=None
        self.buf=""
        #self.js_name=""
        self.num_axis=0
        self.num_buttons=0
        self.axis_states = {}
        self.button_states = {}
        self.EXIT=False
        self.crash=False

    def connect_to(self, path):
        global axis_name
        global button_names
        
        self.path = path
        self.jsdev = open(self.path, 'rb')
        #ioctl(self.jsdev, 0x80006a13 + (0x10000 * 64), self.buf)
        #self.js_name = self.buf

        self.buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a11, self.buf) # JSIOCGAXES
        self.num_axes = self.buf[0]
        

        self.buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a12, self.buf) # JSIOCGBUTTONS
        self.num_buttons = self.buf[0]

        # Get the axis map.
        self.buf = array.array('B', [0] * 0x40)
        ioctl(self.jsdev, 0x80406a32, self.buf) # JSIOCGAXMAP

        for axis in self.buf[:self.num_axes]:
            axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self.axis_map.append(axis_name)
            self.axis_states[axis_name] = 0.0

        # Get the button map.
        self.buf = array.array('H', [0] * 200)
        ioctl(self.jsdev, 0x80406a34, self.buf) # JSIOCGBTNMAP

        for btn in self.buf[:self.num_buttons]:
            btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.button_map.append(btn_name)
            self.button_states[btn_name] = 0

    def info(self):
        print('Device name: %s' % self.path)
        print ('%d axes found: %s' % (self.num_axes, ', '.join(self.axis_map)))
        print ('%d buttons found: %s' % (self.num_buttons, ', '.join(self.button_map)))

    def clear(self):
        self.path=None
        self.axis_map = []
        self.button_map = []
        self.jsdev=None
        self.buff=""
        self.js_name=""
        self.num_axis=0
        self.num_buttons=0
        self.axis_states = {}
        self.button_states = {}
        self.crash=False

    def read(self):
            try:
                evbuf = self.jsdev.read(8)
            except OSError:                
                print("Joystic crash")
                self.crash=True
                time.sleep(2)
            else:                    
                if evbuf:
                    #print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
                    time0, value, type, number = struct.unpack('IhBB', evbuf)
                        
                    if type & 0x80:            
                        print ("initial")
                            
                    if type & 0x01:
                        button = self.button_map[number]
                        if button:
                            self.button_states[button] = value

                    if type & 0x02:
                        axis = self.axis_map[number]
                        if axis:
                            fvalue = value/32767.0
                            self.axis_states[axis] = fvalue
                            
            
                
                
    def get_axis_data(self):
        if(not self.crash):
            return self.axis_states
        else:
            return None

    def get_button_data(self):
        if(not self.crash):
            return self.button_states
        else:
            return None


class Joystick_master(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.Joystick_list=[]
        self.connection=False
        self.EXIT=False
        

    def find_joy(self):
        while(not self.EXIT):
            self.Joystick_list=[]
            for fn in os.listdir('/dev/input'):
                if fn.startswith('js'):
                    self.Joystick_list.append('/dev/input/'+fn)
                    
            if (len(self.Joystick_list)==0):
                self.connection=False
                print("No Joystick found")
                
            time.sleep(5)

    def run(self):
        t=threading.Thread(target=self.find_joy)
        t.start()
        self.JS=Joystick()
        while(not self.EXIT):
            if(not self.connection):
                self.JS.clear()
                if (len(self.Joystick_list)!=0):
                    self.JS.connect_to(self.Joystick_list[0])
                    self.connection=True
                    self.JS.info()
                time.sleep(1)
                    
            else:
                self.JS.read()                

                
    def get_axis(self):
        if(self.connection):
            return self.JS.get_axis_data()
        else:
            return None
        
    def get_button(self):
        if(self.connection):
            return self.JS.get_button_data()
        else:
            return None
        
    def Exit(self):
        self.EXIT=True
    

"""
J=Joystick_master()
J.start()
i=0.0
while(i<1000.0):
    print(J.get_axis())
    time.sleep(0.5)
    i=i+1.0
time.sleep(30)
J.Exit()
"""

