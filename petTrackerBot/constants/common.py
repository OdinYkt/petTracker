import os
from datetime import time

from environs import Env

env = Env()
env.read_env()

IS_LINUX = True if os.name != 'nt' else False

DEBUG_MODE = env.bool('DEBUG_MODE', False)
DEBUG_HEADLESS_BROWSER = env.bool('DEBUG_HEADLESS_BROWSER', False)


TOKEN_BOT = env.str('TOKEN_BOT', None)

ENABLE_POSTING_TG = env.bool('ENABLE_POSTING_TG', False)

POST_TIME = time(hour=7)

# Различные задержки
WRITE_TIMEOUT = 30

SLEEP_BEFORE_REPLY = 1
SLEEP_BETWEEN_POSTS = 2
SLEEP_WHEN_ERROR = 30
