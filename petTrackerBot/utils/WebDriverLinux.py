import os
import threading
import time
import uuid
from functools import wraps
from pathlib import Path

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from undetected_chromedriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

from TgBot.constants.common import IS_LINUX, DEBUG_HEADLESS_BROWSER
from TgBot.constants.paths import paths
from TgBot.utils.common import app_logger, get_traceback

if IS_LINUX:
    from xvfbwrapper import Xvfb


def ONLY_LINUX(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        if IS_LINUX:
            return func(*args, **kwargs)
    return _wrapper


class WebDriverLinux:
    _lock = threading.Lock()

    def __init__(self):
        self.download_dir = paths.get_new_download_dir()
        self.vdisplay: Xvfb = None
        self._driver: uc.Chrome = None
        self.init()

    def _get_driver(self) -> uc.Chrome:
        options = ChromeOptions()
        is_headless = False
        if IS_LINUX:
            is_headless = True
        if DEBUG_HEADLESS_BROWSER:
            app_logger.critical('DEBUG HEADLESS BROWSER')
            is_headless = True
        perfs = {
            "download.default_directory": str(self.download_dir),
            "download.directory_upgrade": True,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True,
            "intl.accept_languages": "en",
        }
        options.add_experimental_option("prefs", perfs)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--prerender-from-omnibox=disabled")

        if is_headless:
            options.add_argument("--headless=new")

        return uc.Chrome(options=options, driver_executable_path=ChromeDriverManager().install())

    @ONLY_LINUX
    def init(self):
        self.vdisplay = Xvfb()

    @ONLY_LINUX
    def start(self):
        # os.environ['DISPLAY'] = ':0'
        self.vdisplay.start()

    @ONLY_LINUX
    def stop(self):
        try:
            self.vdisplay.stop()
        except Exception as e:
            app_logger.critical(f'Ошибка при остановке Xvfb: {e}\n{get_traceback(e)}')

    def __enter__(self) -> WebDriver:
        app_logger.debug('Enabling browser')
        with self._lock:
            self.start()
            time.sleep(3)
            self._driver = self._get_driver()
            self._driver.implicitly_wait(time_to_wait=15)
        return self._driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        app_logger.debug('Stopping browser')
        with self._lock:
            self._driver.quit()
            self.stop()
