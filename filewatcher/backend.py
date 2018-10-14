import logging
import sys
import warnings
from argparse import ArgumentParser

from systemd import daemon, journal

log = logging.getLogger(__name__)

READY = daemon.Notification.READY


def setup_logging(debug):
    """
    Настраивает логгирование

    :param debug:
    :return:
    """
    logging.raiseExceptions = False
    if debug:
        logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stderr)])
    else:
        logging.basicConfig(level=logging.INFO, handlers=[journal.JournaldLogHandler()])

    # Включаем отображение DeprecationWarning
    warnings.simplefilter('always', DeprecationWarning)
    logging.captureWarnings(True)


def systemd_notify(*args, **kwargs):
    """
    Уведомляет systemd о том, что демон успешно запустился, перезапустился и тп. см. документацию к sd_notify.

    :param args:
    :param kwargs:
    :return:
    """
    if not daemon.notify(*args, **kwargs):
        log.warning('Forgot to set Type=notify in systemd service file?')


def default_arg_parser(prog):
    """
    Парсер аргументов по-умолчанию для бакендов

    :param prog:
    :return:
    """
    parser = ArgumentParser(prog)
    parser.add_argument('--debug', default=False, action='store_true', help='Debug mode')

    return parser.parse_args()
