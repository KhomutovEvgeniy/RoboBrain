#!/usr/bin/python3

from Robot import *
import math
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
#https://stackoverflow.com/questions/39553371/how-to-update-drawing-area-in-gtk
intSummValue = 0
currentParrotValue = 0
setParrotValue = 0
pParrotValue = 0
iParrotValue = 0
dParrotValue = 0
resPWMValue = 0

# Рисование ведется в кайро (cairo). Методы рисования есть тут https://python-scripts.com/pycairo-backends-pdf-swg-gtk
# Для сохранения графиков можно использовать следующий метод: Метод write_to_png() записывает содержимое поверхности в изображение PNG. 

class DrawWindow(Gtk.Window):

    def __init__(self):
        super(DrawWindow, self).__init__()

        # Коэффициент масштаба графика. Сколько в одной еденице значения пикселей
        self.graphKoeff = 1

        # Частота отрисовки. Примерно равна кол-ву кадров в секунду
        self.drawFrequency = 7

        self.clearFlag = False
        
        self.width, self.height = 920, 520 # Для корректного отображения шкал необходимо указывать размеры кратные 10, не более 920*520
        self.i = 0
        self.coordsIntSumm = []
        self.coordsCurrentParrot = []
        self.coordsSetParrot = []
        self.coordsPParrot = []
        self.coordsIParrot = []
        self.coordsDParrot = []
        self.coordsResPWM = []

        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.onDraw)
        self.add(self.darea)
        
        self.set_title("Params")
        self.resize(self.width, self.height)
        
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()
        DrC = threading.Thread(target = self.drawingCycle)
        DrC.start()

    def onDraw(self, wid, cr):

        self.cr = cr

        global intSummValue, currentParrotValue, setParrotValue, pParrotValue, iParrotValue, dParrotValue, resPWMValue

        self.webcolor = (0.8, 0.8, 0.8) # Цвет сетки
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(2)

        # Отрисовка рамки
        cr.line_to(0, self.height)
        cr.line_to(0, 0)
        cr.line_to(self.width*2, 0)
        cr.line_to(self.width*2, self.height)
        cr.line_to(0, self.height)
        cr.line_to(0, self.height*2)
        cr.line_to(self.width*2, self.height*2)
        cr.line_to(self.width*2, self.height)
        cr.stroke()

       
        for i in range(self.width*2//10): # Шкала времени в секундах (накапливает ошибку в несколько процентов. за десять секунд запоздает примерно на 0,1 секунды) 

            # Отрисовка сетки

            if i>5:

                cr.set_source_rgb(*self.webcolor)
                cr.move_to(i*10, self.height)
                cr.line_to(i*10, 0)
                cr.move_to(i*10, self.height)
                cr.line_to(i*10, self.height*2)
                cr.stroke()

            # Отрисовка делений

            cr.set_source_rgb(0, 0, 0)

            cr.move_to(i*10, self.height)
            cr.line_to(i*10, self.height-10)
            cr.stroke()

            # Отрисовка крупных делений и чисел
            
            if (i-2)/10 == (i-2)//10 and (i-2)!=0: # (i-2) вводится для того чтобы отложить отрисовку на два круга цикла.Это помогает избежать прорисовки линий поверх цифр
                cr.move_to((i-2)*10, self.height)
                cr.line_to((i-2)*10, self.height-15)

                cr.set_font_size(18)
                cr.move_to((i-2)*10, self.height-20)
                cr.show_text(str(int((i-2)*10/self.drawFrequency)))

                cr.stroke()
                
                cr.set_source_rgb(0.7, 0.7, 0.7)
                cr.move_to((i-2)*10, self.height*2)
                cr.line_to((i-2)*10, 0)

                cr.stroke()

       
        for i in range(self.height//10): # Шкала значений заданного параметра. В одном деление 10 пикселей и 5 едениц значения параметра

            # Отрисовка сетки

            if i>3:

                cr.set_source_rgb(*self.webcolor)
                cr.move_to(0, self.height-i*10)
                cr.line_to(self.width*2, self.height-i*10)

                cr.move_to(0, self.height+i*10)
                cr.line_to(self.width*2, self.height+i*10)
                cr.stroke()


            # Отрисовка делений

            cr.set_source_rgb(0, 0, 0)
            cr.move_to(0, self.height-i*10)
            cr.line_to(10, self.height-i*10)
            cr.move_to(0, self.height+i*10)
            cr.line_to(10, self.height+i*10)
            cr.stroke()

            # Отрисовка крупных делений и чисел

            if (i-2)/10 == (i-2)//10 and (i-2)!=0:
                cr.move_to(0, self.height-(i-2)*10)
                cr.line_to(15, self.height-(i-2)*10)
                cr.move_to(0, self.height+(i-2)*10)
                cr.line_to(15, self.height+(i-2)*10)

                cr.set_font_size(18)
                cr.move_to(20, self.height-(i-2)*10)
                cr.show_text(str(int((i-2)*10/self.graphKoeff)))

                cr.move_to(20, self.height+(i-2)*10)
                cr.show_text(str(int(-(i-2)*10/self.graphKoeff)))

                cr.stroke()
                
                cr.set_source_rgb(0.7, 0.7, 0.7)
                cr.move_to(0, self.height-(i-2)*10)
                cr.line_to(self.width*2, self.height-(i-2)*10)
                cr.move_to(0, self.height+(i-2)*10)
                cr.line_to(self.width*2, self.height+(i-2)*10)

                cr.stroke()

        # Отрисовка Лейбла
        cr.set_source_rgb(0, 0.5, 1)
        cr.set_font_size(20)
        cr.move_to(self.width/2-100,20)
        cr.show_text('Kostyil Production')
        cr.stroke()

        # Отрисовка справочной информации
        
        cr.set_font_size(18)
        
        cr.set_source_rgb(1, 1, 1)
        cr.set_line_width(165)
        cr.move_to(60, 88)
        cr.line_to(200, 88)        
        cr.stroke()

        cr.set_source_rgb(1, 0, 0)
        cr.move_to(70, 28)
        cr.show_text('IntSumm')
        cr.stroke()

        cr.set_source_rgb(0, 0, 1)
        cr.move_to(70, 50)
        cr.show_text('CurrentParrot')
        cr.stroke()

        cr.set_source_rgb(0, 1, 0)
        cr.move_to(70, 72)
        cr.show_text('pParrot')
        cr.stroke()

        cr.set_source_rgb(0.61, 0.43, 0.31)
        cr.move_to(70, 94)
        cr.show_text('iParrot')
        cr.stroke()

        cr.set_source_rgb(15/255, 240/255, 240/255)
        cr.move_to(70, 116)
        cr.show_text('dParrot')
        cr.stroke()

        cr.set_source_rgb(0, 0, 0)
        cr.move_to(70, 138)
        cr.show_text('SetSpeed')
        cr.stroke()

        cr.set_source_rgb(252/255, 15/255, 192/255)
        cr.move_to(70, 160)
        cr.show_text('ResPWM')
        cr.stroke()
                
        # Отрисовка значений параметров

        cr.set_line_width(2)
        
        # IntSumm Красный
        cr.set_source_rgb(1, 0, 0)

        self.coordsIntSumm.append([self.i, intSummValue*self.graphKoeff]) 
        for positions in self.coordsIntSumm:
            cr.line_to(positions[0], int(self.height - positions[1]))
        cr.stroke()

        # CurrentParrot Синий
        cr.set_source_rgb(0, 0, 1)
        self.coordsCurrentParrot.append([self.i, currentParrotValue*self.graphKoeff]) # Значение умножается на два, так как в двух пикселях одна еденица значения
        for positions in self.coordsCurrentParrot:
            cr.line_to(positions[0], int(self.height - positions[1]))
        cr.stroke()

        # pParrot Ярко-Зеленый
        cr.set_source_rgb(0, 1, 0)
        self.coordsPParrot.append([self.i, pParrotValue*self.graphKoeff]) # Значение умножается на два, так как в двух пикселях одна еденица значения
        for positions in self.coordsPParrot:
            cr.line_to(positions[0], int(self.height - positions[1]))
        cr.stroke()

        # iParrot Коричневый
        cr.set_source_rgb(0.61, 0.43, 0.31)
        self.coordsIParrot.append([self.i, iParrotValue*self.graphKoeff]) # Значение умножается на два, так как в двух пикселях одна еденица значения
        for positions in self.coordsIParrot:
            cr.line_to(positions[0], int(self.height - positions[1]))
        cr.stroke()

        # dParrot Голубой
        cr.set_source_rgb(15/255, 240/255, 240/255)
        self.coordsDParrot.append([self.i, dParrotValue*self.graphKoeff]) # Значение умножается на два, так как в двух пикселях одна еденица значения
        for positions in self.coordsDParrot:
            cr.line_to(positions[0], int(self.height - positions[1]))
        cr.stroke()

        # SetSpeed Заданная скорость. Черный
        cr.set_source_rgb(0, 0, 0)
        self.coordsSetParrot.append([self.i, setParrotValue*self.graphKoeff]) # Значение умножается на два, так как в двух пикселях одна еденица значения
        for positions in self.coordsSetParrot:
            cr.line_to(positions[0], int(self.height - positions[1]))
        cr.stroke()

        # ResPWM Розовый
        cr.set_source_rgb(252/255, 15/255, 192/255)
        self.coordsResPWM.append([self.i, resPWMValue*self.graphKoeff]) # Значение умножается на два, так как в двух пикселях одна еденица значения
        for positions in self.coordsResPWM:
            cr.line_to(positions[0], int(self.height - positions[1]))
        cr.stroke()

        self.i+=1

    def clearArea(self): # Вызов возможен только если функция onDraw вызывалась хотя бы раз
        self.i = 0
        self.coordsIntSumm = []
        self.coordsCurrentParrot = []
        self.coordsSetParrot = []
        self.coordsPParrot = []
        self.coordsIParrot = []
        self.coordsDParrot = []
        self.coordsResPWM = []

    def drawingCycle(self):
        while True:
            time.sleep(1/self.drawFrequency)
            self.darea.queue_draw()


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="RoboSettings")
        #self.set_size_request(200,200)
        grid = Gtk.Grid()
        grid.set_column_spacing(6) # Межстолбцовое расстояние
        grid.set_row_spacing(6) # Межстрочное расстояние
        self.add(grid)
        self.GraphicFlag = 0

        # Блокиратор для полей вывода parrot и encoder
        self.blockedParrot = False
        self.blockedEncoder = False

        # Defines

        self.MotorNumber = 0
        
        # Buttons

        # Address
        self.buttonAddr = Gtk.Button(label=" Controller Addr ")
        self.buttonAddr.connect("clicked", self.onControllerMotorClicked)
        grid.attach(self.buttonAddr, 1, 0, 1, 1)

        self.entryAddr = Gtk.Entry()
        self.entryAddr.set_text('0')
        grid.attach(self.entryAddr, 2, 0, 1, 1)

        # Motor Number
        
        self.buttonMotorNumber = Gtk.Button(label=" Motor Number ")
        self.buttonMotorNumber.connect("clicked", self.onMotorNumberClicked)
        grid.attach(self.buttonMotorNumber, 3, 0, 1, 1)

        self.entryMotorNumber = Gtk.Entry()
        self.entryMotorNumber.set_text('0')
        grid.attach(self.entryMotorNumber, 4, 0, 1, 1)


        # PID Coefficients
        self.buttonPropCoef = Gtk.Button(label=" Proportional ")
        self.buttonPropCoef.connect("clicked", self.onPropClicked)
        grid.attach(self.buttonPropCoef, 0, 2, 1, 1)

        self.entryPropCoef = Gtk.Entry()
        self.entryPropCoef.set_text('Unknown')
        grid.attach(self.entryPropCoef, 1, 2, 1, 1)

        self.buttonIntCoef = Gtk.Button(label=" Integral ")
        self.buttonIntCoef.connect("clicked", self.onIntClicked)
        grid.attach(self.buttonIntCoef, 2, 2, 1, 1)

        self.entryIntCoef = Gtk.Entry()
        self.entryIntCoef.set_text('Unknown')
        grid.attach(self.entryIntCoef, 3, 2, 1, 1)

        self.buttonDerCoef = Gtk.Button(label=" Derivative ")
        self.buttonDerCoef.connect("clicked", self.onDerClicked)
        grid.attach(self.buttonDerCoef, 4, 2, 1, 1)

        self.entryDerCoef = Gtk.Entry()
        self.entryDerCoef.set_text('Unknown')
        grid.attach(self.entryDerCoef, 5, 2, 1, 1)

        # Limit summ
        self.buttonLimitSumm = Gtk.Button(label=" Limit Summ ")
        self.buttonLimitSumm.connect("clicked", self.onLimitSummClicked)
        grid.attach(self.buttonLimitSumm, 0, 3, 1, 1)

        self.entryLimitSumm = Gtk.Entry()
        self.entryLimitSumm.set_text('Unknown')
        grid.attach(self.entryLimitSumm, 1, 3, 1, 1)

        # Time PID
        self.buttonTimePID = Gtk.Button(label=" Time PID ")
        self.buttonTimePID.connect("clicked", self.onTimePIDClicked)
        grid.attach(self.buttonTimePID, 2, 3, 1, 1)

        self.entryTimePID = Gtk.Entry()
        self.entryTimePID.set_text('Unknown')
        grid.attach(self.entryTimePID, 3, 3, 1, 1)

        # Time PWM
        self.buttonTimePWM = Gtk.Button(label=" Time PWM ")
        self.buttonTimePWM.connect("clicked", self.onTimePWMClicked)
        grid.attach(self.buttonTimePWM, 4, 3, 1, 1)

        self.entryTimePWM = Gtk.Entry()
        self.entryTimePWM.set_text('Unknown')
        grid.attach(self.entryTimePWM, 5, 3, 1, 1)

        # PWM DeadZone
        self.buttonPWMDeadZone = Gtk.Button(label=" PWM DeadZone ")
        self.buttonPWMDeadZone.connect("clicked", self.onPWMDeadZoneClicked)
        grid.attach(self.buttonPWMDeadZone, 0, 4, 1, 1)

        self.entryPWMDeadZone = Gtk.Entry()
        self.entryPWMDeadZone.set_text('Unknown')
        grid.attach(self.entryPWMDeadZone, 1, 4, 1, 1)

        # AccelBreak step
        self.buttonAccelbreakStep = Gtk.Button(label=" AccelbreakStep ")
        self.buttonAccelbreakStep.connect("clicked", self.onAccelbreakStepClicked)
        grid.attach(self.buttonAccelbreakStep, 2, 4, 1, 1)

        self.entryAccelbreakStep = Gtk.Entry()
        self.entryAccelbreakStep.set_text('Unknown')
        grid.attach(self.entryAccelbreakStep, 3, 4, 1, 1)

        # Emergency level
        self.buttonEmergencyLvl = Gtk.Button(label=" Emergency lvl ")
        self.buttonEmergencyLvl.connect("clicked", self.onEmergencyLvlClicked)
        grid.attach(self.buttonEmergencyLvl, 4, 4, 1, 1)

        self.entryEmergencyLvl = Gtk.Entry()
        self.entryEmergencyLvl.set_text('Unknown')
        grid.attach(self.entryEmergencyLvl, 5, 4, 1, 1)

        # Get All Important Params
        self.buttonGAID = Gtk.Button(label=" Get All Important Params ")
        self.buttonGAID.connect("clicked", self.GAID)
        grid.attach(self.buttonGAID, 0, 10, 6, 1)


        # Controlling Buttons

        self.setSpeed1Label = Gtk.Label('Set Speed1')
        grid.attach(self.setSpeed1Label, 2, 11, 1, 1)

        self.buttonGraphics = Gtk.Button(label=" Graphics ")
        self.buttonGraphics.connect("clicked", self.onGraphicsClicked)
        grid.attach(self.buttonGraphics, 0, 12, 3, 1)

        self.buttonGraphicsRefresh = Gtk.Button(label=" Refresh Graphic ")
        self.buttonGraphicsRefresh.connect("clicked", self.onGraphicsRefreshClicked)
        grid.attach(self.buttonGraphicsRefresh, 3, 12, 3, 1)

        self.buttonWriteInEPROM = Gtk.Button(label=" WRITE IN EPROM ")
        self.buttonWriteInEPROM.connect("clicked", self.onWriteInEPROMClicked)
        grid.attach(self.buttonWriteInEPROM, 1, 13, 2, 1)

        self.buttonReadFromEPROM = Gtk.Button(label=" READ FROM EPROM ")
        self.buttonReadFromEPROM.connect("clicked", self.onReadFromEPROMClicked)
        grid.attach(self.buttonReadFromEPROM, 3, 13, 2, 1)

        # Labels

        self.LabelSetWorkMode = Gtk.Label(" Set Work Mode ")
        grid.attach(self.LabelSetWorkMode, 0, 11, 1, 1)

        # Опционально
        '''
        self.labelPParrot1 = Gtk.Label('pParrot1')
        grid.attach(self.labelPParrot1, 0, 6, 1, 1)
        self.entryPParrot1 = Gtk.Entry()
        self.entryPParrot1.set_text('Unknown')
        grid.attach(self.entryPParrot1, 1, 6, 1, 1)
                    
        self.labelIParrot1 = Gtk.Label('iParrot1')
        grid.attach(self.labelIParrot1, 2, 6, 1, 1)
        self.entryIParrot1 = Gtk.Entry()
        self.entryIParrot1.set_text('Unknown')
        grid.attach(self.entryIParrot1, 3, 6, 1, 1)

        self.labelDParrot1 = Gtk.Label('dParrot1')
        grid.attach(self.labelDParrot1, 4, 6, 1, 1)
        self.entryDParrot1 = Gtk.Entry()
        self.entryDParrot1.set_text('Unknown')
        grid.attach(self.entryDParrot1, 5, 6, 1, 1)

        self.labelResPWM1 = Gtk.Label('resPWM1')
        grid.attach(self.labelResPWM1, 0, 7, 1, 1)
        self.entryResPWM1 = Gtk.Entry()
        self.entryResPWM1.set_text('Unknown')
        grid.attach(self.entryResPWM1, 1, 7, 1, 1)'''

        self.labelCurrentParrot1 = Gtk.Label('Current Parrot')
        grid.attach(self.labelCurrentParrot1, 2, 7, 1, 1)
        self.entryCurrentParrot1 = Gtk.Entry()
        self.entryCurrentParrot1.set_text('Unknown')
        self.entryCurrentParrot1.set_sensitive(False)
        grid.attach(self.entryCurrentParrot1, 3, 7, 1, 1)

        self.labelEncoderData1 = Gtk.Label('Encoder Data')
        grid.attach(self.labelEncoderData1, 4, 7, 1, 1)
        self.entryEncoderData1 = Gtk.Entry()
        self.entryEncoderData1.set_text('Unknown')
        self.entryEncoderData1.set_sensitive(False)
        grid.attach(self.entryEncoderData1, 5, 7, 1, 1)


        # Опционально

        '''
        self.labelIntSumm1 = Gtk.Label('IntSumm1')
        grid.attach(self.labelIntSumm1, 0, 8, 1, 1)
        self.entryIntSumm1 = Gtk.Entry()
        self.entryIntSumm1.set_text('Unknown')
        grid.attach(self.entryIntSumm1, 1, 8, 1, 1)

        self.labelAdcAverage1 = Gtk.Label('AdcAverage1')
        grid.attach(self.labelAdcAverage1, 2, 8, 1, 1)
        self.entryAdcAverage1 = Gtk.Entry()
        self.entryAdcAverage1.set_text('Unknown')
        grid.attach(self.entryAdcAverage1, 3, 8, 1, 1)

        self.labelSetParrot1 = Gtk.Label('Set Parrot1')
        grid.attach(self.labelSetParrot1, 4, 8, 1, 1)
        self.entrySetParrot1 = Gtk.Entry()
        self.entrySetParrot1.set_text('Unknown')
        grid.attach(self.entrySetParrot1, 5, 8, 1, 1)

        self.labelSetPWM1 = Gtk.Label('Set PWM1')
        grid.attach(self.labelSetPWM1, 0, 9, 1, 1)
        self.entrySetPWM1 = Gtk.Entry()
        self.entrySetPWM1.set_text('Unknown')
        grid.attach(self.entrySetPWM1, 1, 9, 1, 1)'''


        self.workModeStore = Gtk.ListStore(str, int)
        self.workModeStore.append(['Not set', 0])
        self.workModeStore.append(['PID', 1])
        self.workModeStore.append(['PWM', 2])
        self.workModeStore.append(['Pulse', 3])
            
        self.workModeCombo = Gtk.ComboBox.new_with_model(self.workModeStore)
        self.workModeCombo.set_active(0)
        self.workModeCombo.connect("changed", self.onWorkModeComboChanged)
        renderer_text = Gtk.CellRendererText()
        self.workModeCombo.pack_start(renderer_text, True)
        self.workModeCombo.add_attribute(renderer_text, "text", 0)
        grid.attach(self.workModeCombo, 1, 11, 1, 1)

        # Speed Scale

        self.speedScale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Gtk.Adjustment(0, -255, 255, 1, 10, 0))
        self.speedScale.set_digits(0)
        self.speedScale.connect('value-changed', self.onSpeedScaleChanged)
        grid.attach(self.speedScale, 3, 11, 3, 1)
        self.grid = grid # Лень добавлять ко всем гридам селф

        # Check Box for debugInfoMask

        self.debugInfoMaskList = [0, 0, 0, 0, 0]
        
        self.checkBox = Gtk.Box(spacing = 6)
        grid.attach(self.checkBox, 1, 9, 4, 1) 
        self.labelDebugInfoMask = Gtk.Label('DebugInfoMask :')
        self.checkBox.pack_start(self.labelDebugInfoMask, True, True, 0)
        
        self.checkButtonTahometr = Gtk.CheckButton('Tahometr')
        self.checkButtonTahometr.connect('toggled', self.onCheckButtonTahometrClicked)
        self.checkBox.pack_start(self.checkButtonTahometr, True, True, 0)

        self.checkButtonOdometr = Gtk.CheckButton('Odometr')
        self.checkButtonOdometr.connect('toggled', self.onCheckButtonOdometrClicked)
        self.checkBox.pack_start(self.checkButtonOdometr, True, True, 0)

        self.checkButtonFirstMotorData = Gtk.CheckButton('Motor 1 Data')
        self.checkButtonFirstMotorData.connect('toggled', self.onCheckButtonFirstMotorDataClicked)
        self.checkBox.pack_start(self.checkButtonFirstMotorData, True, True, 0)

        self.checkButtonSecondMotorData = Gtk.CheckButton('Motor 2 Data')
        self.checkButtonSecondMotorData.connect('toggled', self.onCheckButtonSecondMotorDataClicked)
        self.checkBox.pack_start(self.checkButtonSecondMotorData, True, True, 0)

        self.checkButtonElectricCurrent = Gtk.CheckButton('ElectricCurrent')
        self.checkButtonElectricCurrent.connect('toggled', self.onCheckButtonElectricCurrentClicked)
        self.checkBox.pack_start(self.checkButtonElectricCurrent, True, True, 0)

        # KOSTYIL

        self.counter1 = 0 # Счетчики для ограничения частоты вывода полей CurrentParrot1 и EncoderData1
        self.counter2 = 0

    def onMotorNumberClicked(self, widget):
        self.MotorNumber = int(self.entryMotorNumber.get_text())
        

    def onWriteInEPROMClicked(self, widget):
        self.CM.SendCommand(0xCA)
        
    def onReadFromEPROMClicked(self, widget):
        self.CM.SendCommand(0xCA)

    def onCheckButtonTahometrClicked(self, widget):
        if self.checkButtonTahometr.get_active():
            self.debugInfoMaskList[0] = 1
        else:
            self.debugInfoMaskList[0] = 0
        self.DebugInfoMaskChanger()

    def onCheckButtonOdometrClicked(self, widget):
        if self.checkButtonOdometr.get_active():
            self.debugInfoMaskList[1] = 1
        else:
            self.debugInfoMaskList[1] = 0
        self.DebugInfoMaskChanger()

    def onCheckButtonFirstMotorDataClicked(self, widget):
        if self.checkButtonFirstMotorData.get_active():
            self.debugInfoMaskList[2] = 1
        else:
            self.debugInfoMaskList[2] = 0
        self.DebugInfoMaskChanger()

    def onCheckButtonSecondMotorDataClicked(self, widget):
        if self.checkButtonSecondMotorData.get_active():
            self.debugInfoMaskList[3] = 1
        else:
            self.debugInfoMaskList[3] = 0
        self.DebugInfoMaskChanger()

    def onCheckButtonElectricCurrentClicked(self, widget):
        if self.checkButtonElectricCurrent.get_active():
            self.debugInfoMaskList[4] = 1
        else:
            self.debugInfoMaskList[4] = 0
        self.DebugInfoMaskChanger()
        
    def DebugInfoMaskChanger(self):
        self.CM.SetDebugInfoMask(*self.debugInfoMaskList)
        
    def DebugInfoMaskChanger2(self): # Просто дублёр, для сохранения содержания функции при её переопределении
        self.CM.SetDebugInfoMask(*self.debugInfoMaskList)

    def onSpeedScaleChanged(self, widget):
        global setParrotValue
        value = self.speedScale.get_value()
        setParrotValue = value
        #print(value)
        self.CM.SetSpeed(self.MotorNumber, int(value))
        time.sleep(0.1)

    def onPWMScaleChanged(self, widget):
        global setParrotValue
        value = self.speedScale.get_value()
        setParrotValue = value
        #print(value)
        self.CM.SetMotorPWM(self.MotorNumber, int(value))
        time.sleep(0.1)
                
    def onWorkModeComboChanged(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            workMode = model[tree_iter][1]
            print("Work mode = %s" % workMode)
            self.CM.SetWorkMode(workMode)
            if workMode == 1:
                self.speedScale.destroy()
                self.speedScale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Gtk.Adjustment(0, -100, 100, 1, 10, 0))
                self.speedScale.set_digits(0)
                self.speedScale.connect('value-changed', self.onSpeedScaleChanged)
                self.grid.attach(self.speedScale, 3, 11, 3, 1)
            elif workMode == 2:
                self.speedScale.destroy()
                self.speedScale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Gtk.Adjustment(0, -255, 255, 1, 10, 0))
                self.speedScale.set_digits(0)
                self.speedScale.connect('value-changed', self.onPWMScaleChanged)
                self.grid.attach(self.speedScale, 3, 11, 3, 1)
            elif workMode == 0 or workMode == 3:
                self.speedScale.set_sensitive(False)

            self.grid.show_all()



    def GAID(self, widget):
        for i in range(40):
            self.CM.SendCommand(0xC8, (i,))
            time.sleep(0.01)
    
    def onControllerMotorClicked(self, widget):
        self.CM = ControllerMotor(Droideka, int(self.entryAddr.get_text()))
        self.CM.onGetParam = self.Raspredelitel
        Droideka.online = True
        time.sleep(0.01)
        # Запросить состояние debugInfoMask
        self.CM.SendCommand(0xC8, (0x01,))
        
    def onPropClicked(self, widget):
        value = float(self.entryPropCoef.get_text())
        self.CM.SendParam(0x02, value)

    def onIntClicked(self, widget):
        value = float(self.entryIntCoef.get_text())
        self.CM.SendParam(0x03, value)

    def onDerClicked(self, widget):
        value = float(self.entryDerCoef.get_text())
        self.CM.SendParam(0x04, value)

    def onLimitSummClicked(self, widget):
        value = int(self.entryLimitSumm.get_text())
        self.CM.SendParam(0x05, value)

    def onTimePIDClicked(self, widget):
        value = int(self.entryTimePID.get_text())
        self.CM.SendParam(0x06, value)

    def onTimePWMClicked(self, widget):
        value = int(self.entryTimePWM.get_text())
        self.CM.SendParam(0x07, value)

    def onPWMDeadZoneClicked(self, widget):
        value = int(self.entryPWMDeadZone.get_text())
        self.CM.SendParam(0x08, value)

    def onAccelbreakStepClicked(self, widget):
        value = int(self.entryAccelbreakStep.get_text())
        self.CM.SendParam(0x09, value)

    def onEmergencyLvlClicked(self, widget):
        value = int(self.entryEmergencyLvl.get_text())
        self.CM.SendParam(0x0A, value)

    def onGraphicsRefreshClicked(self, widget):
        self.dwin.clearArea()

    def onGraphicsClicked(self, widget):
        if not self.GraphicFlag:
            self.dwin = DrawWindow()
            self.GraphicFlag = 1

    def Vacuum(self):
        pass

    def RaspredelitelCall(self, prmNumber, prm):
        threading.Thread(target=self.Raspredelitel, args=(prmNumber, prm)).start()
        #time.sleep(0.07)

    def Raspredelitel(self, prmNumber, prm):
        global intSummValue, currentParrotValue, pParrotValue, iParrotValue, dParrotValue, resPWMValue

        if prmNumber == 0x01:
            self.DebugInfoMaskChanger = self.Vacuum # На время задания галочек в чекбоксы отключаем их функции (т.к. эти функции делают данный цикл не корректным. На каждом этапе функция переопределяет значения дебагинфомаска и отсылает эту информацию в контроллер, он отвечает и заново вызывает эту функцию. А дебагинфомаск должен определяться лишь единажды в конце выполнения этой функции)
            if prm//16 == 1:
                if self.checkButtonElectricCurrent.get_active():
                    pass
                else:
                    self.checkButtonElectricCurrent.set_active(1)
                prm = prm-16
            else:
                self.checkButtonElectricCurrent.set_active(0)

            if prm//8 == 1:
                self.checkButtonSecondMotorData.set_active(1)
                prm = prm-8
            else:
                self.checkButtonSecondMotorData.set_active(0)

            if prm//4 == 1:
                self.checkButtonFirstMotorData.set_active(1)
                prm = prm-4
            else:
                self.checkButtonFirstMotorData.set_active(0)

            if prm//2 == 1:
                if self.checkButtonOdometr.get_active():
                    pass
                else:
                    self.checkButtonOdometr.set_active(1)
                prm = prm-2
            else:
                self.checkButtonOdometr.set_active(0)

            self.DebugInfoMaskChanger = self.DebugInfoMaskChanger2 

            if prm == 1:
                if self.checkButtonTahometr.get_active():
                    pass
                else:
                    self.checkButtonTahometr.set_active(1)
            if prm == 0: 
                self.checkButtonTahometr.set_active(0)

        elif prmNumber == 0x02:
            if self.entryPropCoef.get_text() != prm:
                self.entryPropCoef.set_text(str(prm))
        elif prmNumber == 0x03:
            if self.entryIntCoef.get_text() != prm:
                self.entryIntCoef.set_text(str(prm))
        elif prmNumber == 0x04:
            if self.entryDerCoef.get_text() != prm:
                self.entryDerCoef.set_text(str(prm))
        elif prmNumber == 0x05:
            if self.entryLimitSumm.get_text() != prm:
                self.entryLimitSumm.set_text(str(prm))
        elif prmNumber == 0x06:
            if self.entryTimePID.get_text() != prm:
                self.entryTimePID.set_text(str(prm))
        elif prmNumber == 0x07:
            if self.entryTimePWM.get_text() != prm:
                self.entryTimePWM.set_text(str(prm))
        elif prmNumber == 0x08:
            if self.entryPWMDeadZone.get_text() != prm:
                self.entryPWMDeadZone.set_text(str(prm))
        elif prmNumber == 0x09:
            if self.entryAccelbreakStep.get_text() != prm:
                self.entryAccelbreakStep.set_text(str(prm))
        elif prmNumber == 0x0A:
            if self.entryEmergencyLvl.get_text() != prm:
                self.entryEmergencyLvl.set_text(str(prm))

        # Индивидуальные для моторов

        elif prmNumber == 0x15 + 0x0A*self.MotorNumber:
            #if self.entryPParrot1.get_text() != prm:
                #self.entryPParrot1.set_text(str(prm))
            pParrotValue = prm

        elif prmNumber == 0x16 + 0x0A*self.MotorNumber:
            #if self.entryIParrot1.get_text() != prm:
                #self.entryIParrot1.set_text(str(prm))
            iParrotValue = prm
            
        elif prmNumber == 0x17 + 0x0A*self.MotorNumber:
            #if self.entryDParrot1.get_text() != prm:
                #self.entryDParrot1.set_text(str(prm))
            dParrotValue = prm
        
        elif prmNumber == 0x18 + 0x0A*self.MotorNumber:
            #if self.entryResPWM1.get_text() != prm:
                #self.entryResPWM1.set_text(str(prm))
            resPWMValue = prm
            
        elif prmNumber == 0x19 + 0x0A*self.MotorNumber:
            if self.entryCurrentParrot1.get_text() != prm:
                currentParrotValue = prm
                if self.counter1 == 1:
                    self.SetTextParrot(self.entryCurrentParrot1, prm)
                    self.counter1 = 0
                else:
                    self.counter1 += 1
                

        elif prmNumber == 0x1A + 0x0A*self.MotorNumber:
            if self.entryEncoderData1.get_text() != prm:
                if self.counter2 == 1:
                    self.SetTextEncoder(self.entryEncoderData1, prm)
                    self.counter2 = 0
                else:
                    self.counter2 += 1

        elif prmNumber == 0x1B + 0x0A*self.MotorNumber:
            #if self.entryIntSumm1.get_text() != prm:
                #self.entryIntSumm1.set_text(str(prm))
            intSummValue = prm

        '''elif prmNumber == 0x1C:
            if self.entryAdcAverage1.get_text() != prm:
                self.entryAdcAverage1.set_text(str(prm))
        elif prmNumber == 0x1D:
            if self.entrySetParrot1.get_text() != prm:
                self.entrySetParrot1.set_text(str(prm))
        elif prmNumber == 0x1E:
            if self.entrySetPWM1.get_text() != prm:
                self.entrySetPWM1.set_text(str(prm))'''
        #time.sleep(0.07)
        
    def SetTextParrot(self, widget, prm): # Обращение к полям вывода по функциям сделано для того чтобы ограничить возможности одновременного обращения к полю вывода нескольких обьектов 
        if not self.blockedParrot:
            self.blockedParrot = True
            widget.set_text(str(prm))
            widget.show_all()
            time.sleep(0.05)
            self.blockedParrot = False
            
    def SetTextEncoder(self, widget, prm): # Обращение к полям вывода по функциям сделано для того чтобы ограничить возможности одновременного обращения к полю вывода нескольких обьектов 
        if not self.blockedEncoder:
            self.blockedEncoder = True
            widget.set_text(str(prm))
            widget.show_all()
            time.sleep(0.05)
            self.blockedEncoder = False

            
Droideka = Robot('can0')

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

# ЦВЕТА НА ГРАФИКЕ

        # CurrentParrot Синий

        # pParrot Ярко-Зеленый

        # iParrot Коричневый

        # dParrot Голубой

        # SetSpeed Заданная скорость. Черный


# З.Ы. Если вы чего-то не понимаете в коде, не переживайте - он тоже вас не понимает.
