""" Тестовый пример использования модулей проекта RoboBrain """

#!/usr/bin/env python3

""" Для работы необходимо импортировать содержимое файла Robot.py """
from Robot import *
""" Так же необходимо, чтобы в одной папке с программой, использующий модуль RoboBrain находился файл Robot.py, 
файл ControllerBase.py, и файлы названия которых соответствуют типам используемых вами контроллеров """

""" В первую очередь создается объект класса Robot, в качестве параметра указывается название используемой кэн-шины """
Rube = Robot('can0') 

""" Затем создается объект класса Controller***, с помощью которого будет управляться используемый контроллер
Например, я хочу использовать контроллер моторов с адресом 0х201, тогда я создаю объект класса ControllerMotor. 
В качестве параметров указывается объект класса Robot, а так же адрес контроллера (к указаному прибавляется 0x200), 
по умолчанию параметр адреса равен нулю. """
CM = ControllerMotor(Rube, 1)
""" На данный момент существует три типа контроллеров: 
Контроллер моторов, контроллер сервоприводов и контроллер шаговых двигателей. """

""" Включаем отправку онлайн меток. Онлайн метка - специальное сообщение (с номером 0x500), 
посылаемое на контроллер для проверки связи. Если на контроллер несколько секунд подряд не приходит онлайн метка, 
то он прекращает выполнение команд. """
Rube.online = True

""" Выставляем режим работы контроллера. 0 - режим не задан, 1 - ПИД режим, 2 - ШИМ режим """
CM.SetWorkMode(1)

""" Для контролирования моторов в ПИД режиме используется следующая команда:
где, первый параметр - номер мотора (0 либо 1), 
второй параметр - значение задаваемой скорости в попугаях(настраиваемая относительная величина) от -100 до 100 """
CM.SetSpeed(1, 20)

""" Даем роботу покрутить мотор 1 со скорость 20 попугаев 5 секунд """
time.sleep(5)

""" Останавливаем мотор """
CM.SetSpeed(1, 0)

""" Изменяем режим работы на ШИМ """
CM.SetWorkMode(2)

""" Задаем мотору 0 ШИМ 220. Первый параметр - номер мотора (0 либо 1), 
второй параметр - значение ШИМ от -255 до 255 """
CM.SetMotorPWM(0, 220)

""" Даем роботу покрутить мотор 0 с ШИМом 220 попугаев 5 секунд """
time.sleep(5)

""" Задаем режим работы 0 - "не задан" """
CM.SetWorkMode(0)
