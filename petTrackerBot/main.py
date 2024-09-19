from datetime import datetime, timezone

from petTrackerBot.MasterBot import MasterBot
from petTrackerBot.constants.common import DEBUG_MODE
from petTrackerBot.utils.app_state import APP_STATE
from petTrackerBot.utils.common import app_logger


if __name__ == '__main__':
    app_logger.info('Запуск...')
    if DEBUG_MODE:
        APP_STATE.clear_state()
    app_logger.critical(f'DEBUG MODE: {DEBUG_MODE}')

    if not APP_STATE.FIRST_STARTED:
        APP_STATE.FIRST_STARTED = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M:%S")
    APP_STATE.SCHEDULER_CREATED = False

    master_bot = MasterBot()
    master_bot.run_application()
