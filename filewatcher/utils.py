import ipaddress
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
