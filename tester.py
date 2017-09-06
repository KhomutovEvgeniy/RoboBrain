# Из кортежа в список и обратно (Работает)
'''
a = ((1, 2, 3),  (3, 4, 5))
b = [list(a[0]),list(a[1])]
print(b)
b[0][2] = 15
a = (tuple(b[0]), tuple(b[1]))
print(a)'''


# Проверка приватности переменных (Работает)
'''class GladToSeeYou():
    def __init__(self):

        self.Albatros = 15

        self.__Aist = 9

G = GladToSeeYou()
print(G.Albatros)
print(G.__Aist)'''

# Попытка изменять переменную в функции (Не работает)
'''def TimeToChange(value):
    value = 4

a = 1
TimeToChange(a)
print(a)'''

# Проверка property(По р-там можно использовать только функции в определении проперти)
'''
class MrProper():

    def __init__(self):
        self.__Moidodir = 16
        self.Moidodir = property(self.__Moidodir)


    def GetMoidodir(self):
        return self.__Moidodir


Mr = MrProper()
print(Mr.Moidodir)'''

# Можно ли из класса наследника обращаться к скрытым элементам предка (не вышло)
'''
class Parent():
    __a = 'lol'
    def __init__(self):
        print(self.__a)    
    
class Child(Parent):
    def __init__(self):
        Parent.__init__(self)

    def Printer(self):
        print(__a)
    
C = Child()
C.Printer()'''

# Как корректно дополнить наследуемую функцию

'''class Parent():
    def __init__(self):
        pass

    def func1():
        print('Arbuz')

class Child(Parent):
    def __init__(self):
        pass
    def func1():
        print('Krasivii')
        Parent.func1()

Child.func1()'''

# Можно ли изменить protected переменную (Можно. Протектед - условность)

'''class Gastronom():
    def __init__(self):
        self._arbuz = 3
        self.potato = 5
L = Gastronom()
L._arbuz = 4
print(L._arbuz)'''

# Как работает super
'''
class Parent():
    def __init__(self):
        self.a = 1    
    
class Child(Parent):
    def __init__(self):
        super().__init__()

    def Printer(self):
        print(self.a)
    
C = Child()
C.Printer()'''

# Преобразование кортежа кортежей в список списков
'''
a = ((1,2),(3,4),(5,6))
b = []
for i in a:
    b.append(list(i))
print(b)'''
    
# Проверка работы цикла for
'''
for i in range (2):
    print(i)'''


