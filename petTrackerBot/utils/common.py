import asyncio
import logging
import sys
import traceback

from telegram.error import RetryAfter, TimedOut

from petTrackerBot.constants.common import DEBUG_MODE, SLEEP_WHEN_ERROR
from petTrackerBot.constants.paths import paths


def setup_logger():
    logger = logging.getLogger('TgBotParser')
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_level = logging.DEBUG if DEBUG_MODE else logging.INFO
    console_handler.setLevel(console_level)

    file_handler = logging.FileHandler(str(paths.get_new_log_file()), encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s|%(name)s:%(module)s:%(thread)d|%(levelname)s| %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


app_logger = setup_logger()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_traceback(e: Exception) -> str:
    return ''.join(traceback.format_exception(e))


def retry_on_exception(retries: int = 5, delay: int = SLEEP_WHEN_ERROR):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except RetryAfter as e:
                    last_exception = e
                    app_logger.info(f'Не удалось отправить. Попытка #{attempt}\n'
                                    f'Отловлена ошибка: {str(last_exception)}')
                    await asyncio.sleep(delay)
                except TimedOut as e:
                    last_exception = e
                    app_logger.info('Отловлена ошибка: Timed out')
                    break
            logging.error('Сообщение не отправлено!')
            raise last_exception
        return wrapper
    return decorator
