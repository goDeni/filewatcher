import _thread
import datetime
import ipaddress
import os
import time
from crypt import crypt
from hmac import compare_digest
from os.path import isdir


def enter_positive_number(message: str, enable_exit_message=True, exit_on_empty=False) -> int:
    """
    Функция для ввода не отрицательного числа

    :param exit_on_empty:
    :param message: сообщение перед вводом числа
    :param enable_exit_message: включить сообщение "Enter 0 for exit" перед тем как выведет message
    :return:
    """
    if enable_exit_message:
        print("Press 0 to exit")

    while True:
        try:
            num = input(message)
            if not num and exit_on_empty:
                return 0
            num = int(num)
            if num >= 0:
                return num
            print("The number can not be negative")
        except ValueError:
            print("It isn't a number")


def enter_bool(message: str):
    """
    Функция для ввода bool ответа

    :param message: сообщение приглашающее к вводу
    :return: True/False/None
    """
    while True:
        print("Leave the field blank if you don't want to change it")
        print(message, '[yes/no]', end=': ')
        value = input().lower()
        if not value:
            return None
        elif value in ('yes', 'y', 'да', 'д'):
            return True
        elif value in ('no', 'n', 'нет', 'н'):
            return False


def enter_string(message: str):
    s = input(message)
    while s.startswith(' '):
        s = s[1:]
    while s.endswith(' '):
        s = s[:-1]
    return s


def valid_ip(value: str) -> bool:
    """
    Check ip address to valid
    :param value: str
    :return: bool
    """
    if not isinstance(value, str):
        return False
    try:
        ipaddress.ip_network(value, strict=False)
    except ValueError:
        return False
    return True


def enter_ip(message: str):
    while True:
        ip = enter_string(message)
        if not ip:
            return ip
        if valid_ip(ip):
            return ip
        print("Invalid ip")


def enter_path(message: str) -> str:
    while True:
        path = enter_string(message)
        if not path:
            return ""
        if not path.startswith('/'):
            print("Path is not absolute")
            continue
        if not isdir(path):
            print("Invalid path")
            continue
        return path


def encrypt_password(password: str, hash_=None) -> str:
    """
    Хэшируем пароль

    :param hash_:
    :param password: - str
    :returns : hex str
    """
    if hash_:
        return crypt(password, hash_)
    return crypt(password)


def check_password(password: str, password_hash: str) -> bool:
    """
    Проверяет пароль

    :param password: пароль
    :param password_hash: хэш пароля полученный функцией "encrypt_password"
    :return: правильный ли пароль
    """
    return compare_digest(crypt(password, password_hash), password_hash)


def format_time(time_: float) -> str:
    """
    Форматирует unix-time в читабельный формат

    :param time_: unix-time
    :return: дату в виде 10:00 28.08.2018
    """
    if not time_:
        return "N/A"
    date = datetime.datetime.fromtimestamp(time_)
    return date.strftime('%H:%M %d.%m.%Y')


def human_file_size(bytes_size: float, si_=False) -> str:
    """
    Перводит количество байт в человекочитаемую строку.

    :param bytes_size: Количество байт
    :param si_: СИ
    :return:
    """
    thresh = 1000 if si_ else 1024
    if abs(bytes_size) < thresh:
        return "{} B".format(bytes_size)

    units = ('kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    if not si_:
        units = ('KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')

    i = -1

    while abs(bytes_size >= thresh and i < len(units)-1):
        bytes_size /= thresh
        i += 1

    return "{:.2f} {}".format(bytes_size, units[i])


def get_folder_size(start_path ='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size


def get_three(root: str, folder: str):
    num = len(root)
    if num != 0:
        num += 1
    return [a[0][num:] for a in os.walk(os.path.join(root, folder))][1:]


def get_count_files(dir: str):
    return sum([len(a[2]) for a in os.walk(os.path.join(dir))])


def get_files(directory: str, is_root: bool=False, get_size: bool=False):
    n = len(directory) + 1 if is_root else 0
    for path, dirs, files in os.walk(directory):
        for file in files:
            if get_size:
                yield [os.path.join(path, file)[n:], round(os.path.getsize(os.path.join(path, file)))]
            else:
                yield os.path.join(path, file)[n:]


def get_folders(directory: str, is_root: bool=False, get_size: bool=False):
    n = len(directory) + 1 if is_root else 0
    for path, dirs, files in os.walk(directory):
        for d in dirs:
            if get_size:
                yield os.path.join(path, d)[n:], round(os.path.getsize(os.path.join(path, d)))
            else:
                yield os.path.join(path, d)[n:]


def run_forever(repeat_delay: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            def wrap():
                while True:
                    func(*args, **kwargs)
                    time.sleep(repeat_delay)
            print("Created thread function '{}' with repeat_delay={}".format(func.__name__, repeat_delay))
            _thread.start_new_thread(wrap, ())
        return wrapper
    return decorator
