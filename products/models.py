import jwt
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from datetime import datetime, timedelta


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if email is None:
            raise TypeError('У пользователей должен быть e-mail')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        if password is None:
            raise TypeError('Суперюзер должен иметь пароль')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, db_index=True, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    score = models.ForeignKey(to='Score', on_delete=models.CASCADE, verbose_name='счета', null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp()),
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')


class Products(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название', db_index=True)
    desc = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена')

    def __str__(self):
        return self.name


class Score(models.Model):
    account_id = models.IntegerField(db_index=True, verbose_name='Идентификатор счёта')
    balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Баланс')

    def __str__(self):
        return self.account_id


'''
1)Типы данных:
- изменяемые (словрь, лист, множество)
- неизменяемые (число, строка, кортеж, замороженное множество)
2) Когда какие используем и что сколько веисит
None - 16 byte
int - 32 byte
list [] - 64 byte
tuple () - 48 byte
dict () - 288 byte (python3.5) / 
Когда есть важные данные, которые нельзя изменять - спользуем неизменяемые. Во всех случае, где можно лист заменить кортетжем меняем, т.к меньше занимает памяти
3) Итераторы и генераторы
 Итераторы - объекты, элементы которых можно перебрать 1 за 1 с помощью функции next, когда элементы заканчиваются получаем исключение StopIteration. Если рассматривать итератор как класс, то он имеет 2 магических метода iter и next. Можно написать свой итератор.
 
class MyIterator:
    def __init__(self, iter_obj):
        self.iter_obj = iter_obj
        self.step = 0

    def __iter__(self):
        return self

    def __next__(self):
        step = self.step
        self.step += 1
        try:
            return self.iter_obj[step]
        except IndexError:
            raise StopIteration
 
 
 
 Генератор - объекты, которые генерируют свои элементы на хода, т.е не хранят все значения.Элементы генераторов перебираются так же с помощью функции next. Пример [i for i in range(1100000)] будет ошибка MemoryError, если не хватит ОЗУ ПК. Исправляем ее генератором 
 gen = (i for i in range(11000000)) - генератор выражений
 print(next(gen))#0
 print(next(gen))#1
 
 Функция генератор:
  Используется специальное слово yeild вместо return, оно ставит функции на паузу  и продолжает выполнение при вызове next. 
 def fib_digits(range_):
    prev, curr = 0, 1
    print(prev)
    for _ in range(range_):
        yield curr
        prev, curr = curr, prev + curr


gen = fib_digits(5)
print(f'{next(gen)} - Next one')
print(f'{next(gen)} - Next two')
# for fib_digit in gen:
#   print(fib_digit)
4) ЧТо такое декораторы и как работает, какие бываю
Декоратор - функция, которая изменяем поведение другой функции, осннован на замыкании
Пример декоратор, который  выводит время выполнения функции

Декораторы бывают параметрические и обычные
параметрические примнимаю аргументы, обычные нет.
Пример декоратор, который  выводит время выполнения функции(обычный)
import time


def benchmark(func):
    def wrapper(*args, **kwargs):

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print( start_time - end_time)
        return result

    return wrapper


@benchmark
def qq(qq, b):
    print(qq)
    print(b)


# a = qq('q', b=1)
# print(a)

Параметрический декоратор(вызывает функции кол-во раз, переденное в аргумент iteration и возращает среднее врем выполнения функции)

def get_time(iterations):
    def dec(func):
        def wrapper(*args, **kwargs):
            total = 0
            for _ in range(iterations):
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()
                total += start + end
            total /= iterations
            print(f'Average time is {total}')
            return result

        return wrapper

    return dec


@get_time(10)
def test(a, b):
    sum_ = a + b
    return sum_


# print(test(1, 2))
6)Как вызывать декоратор без собаки?
 bencmark(qq) - вернет объект функции wrapper
 benchmark(qq)('q','g') # вернет результат и выведе на экран время выоплнения функции
 
 7) Что такое контексный менеджер?
  Контестный менеджер нужен для работы с файлами или подобными объектами. Если мы используем open , то после открытия файла нам надо его закрыть file.close(), если не закрыть то он будет в памяти. При использовации with  он сам закрывает файл. ЕСли рассматривать как класс использует 2 магических метода enter  и exit, enter - действия перед октрытие файла, exit  - после закрытия.
  Примеры можно найти в интернетее. Если писать свого менеджера, то можно переопределить enter, exit либо использовать готовый декоратор из from contextlib import contextmanager
  8)  Напиши констекный менеджер для соединия с базой(пример из sqlalchemy)
  from contextlib import contextmanager
from tables import Session


@contextmanager
def connect():
    sess = Session()
    yield sess
    sess.close()
 9) ООП - 3 кита(полиморфизм, инкацплуляция, наследование), декоратор(staticmethod,classmethod, abstractmethod, property), сокрытие данные, магические методы какие знаешь и как понимаешь их работу
 https://python-scripts.com/object-oriented-programming-in-python
 10) Использование памяти питоном(сборщик мусора)
 https://habr.com/ru/post/417215/
 Django/ django rest/базы/ общие
 1) N+1 проблема и как решить.
 Возникает, когда есть вложенность в серилизаторе. ОРМ стучит в доп таблицу, когда достает каждый объект. К примеру 1 вложенность и 100 записей, соотвенно на получение всех записей  будет 101 запрос к базе, 1 - достать все записи и + 1 на каждую запись в другую таблицу. Как избавиться join. select_releated - для FK, prefeatch_releted - для M2M
 2) Индексация в базе данных sql
 https://habr.com/ru/post/247373/
 3) Что такое миксины
 Миксины - готовые классы, которые достают объекты из базы данных, сериализуют  и отдают ответ
 4) Как провалидировать данные в сериализаторе
 def validate_{filed_name}:
 	"""code here"""
 5) Методы create, update  в серилизаторе
 create - вызывает при создании объекта, update - при обновлении
 6) Как передать в запросе лист id так,что создался объект сразу с m2m связими.
 Перезагрузить create, создавать в начале оснновную модель без m2m связей, потом к ней создать связи m2m
 7) ЧТо такое lt, gt, gte, lte в orm
 меньше чем, больше чем, больше либо равно, меньше либо равно
 8) Or  в django orm
 Q  
 9) Какие есть типы Http запросов
 Post, get, delete, put, patch
 10) Отличие протокола Http от Https 
 https://habr.com/ru/post/215117/
 
 
 
 

'''

