import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

from telegram.ext import Application, CallbackContext, JobQueue

from petTrackerBot.petTrackerApp.tables import DBUser
from petTrackerBot.update_map import update_map
from petTrackerBot.db_utils import DbUtils
from petTrackerBot.utils.app_state import APP_STATE
from petTrackerBot.utils.common import app_logger, get_traceback

from petTrackerBot.constants.common import POST_TIME, ENABLE_POSTING_TG


async def restart_scheduler(application: Application):
    if APP_STATE.KEEP_SCHEDULER_ENABLED:
        app_logger.critical('Бот был перезапущен после перезапуска!')
        APP_STATE.LAST_RESTARTED = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M:%S")
        await activate_scheduler(application.job_queue)
        return
    app_logger.critical('Бот запущен без предварительных параметров.')


async def activate_scheduler(job_queue: JobQueue):
    """
    Главный планировщик

    Note:
        * Интервал между запусками задается INTERVAL_HOURS
        * Гарантирована работа только одного экземпляра планировщика
        * Планировщик перезапускается при запуске бота, если включен параметр KEEP_SCHEDULER_ENABLED
    """
    app_logger.info('Активация планировщика')
    if APP_STATE.SCHEDULER_CREATED:
        app_logger.critical('Отказано. Попытка запустить второй планировщик.')
        return
    APP_STATE.SCHEDULER_CREATED = True

    # Убедиться, что перезапуск не заруинил постинг
    # app_logger.info('Запуск таски')
    # await run_tasks()

    job_queue.run_daily(
        run_tasks,
        time=POST_TIME
    )
    app_logger.info(f'Планировщик запущен, постинг в {POST_TIME}')


async def run_tasks(context: Optional[CallbackContext] = None):
    app_logger.info('Запуск задач...')
    try:
        await update_map()
    except Exception as e:
        app_logger.critical(f"Ошибка при запуске задачи на парсинг:\n"
                            f"{get_traceback(e)}")

    try:
        await run_posting_tg()
    except Exception as e:
        app_logger.critical(f"Ошибка при запуске задач на постинг:\n"
                            f"{get_traceback(e)}")


async def run_posting_tg():
    if not ENABLE_POSTING_TG:
        app_logger.critical("Постинг в TG отключен. Задайте переменную окружения ENABLE_POSTING_TG")
        return

    # if DEBUG_MODE:
    #     await change_parsers_target_group(new_group=DEBUG_GROUP_ID)

    from petTrackerBot.MasterBot import MasterBot
    #
    # app_logger.info('Сбор сообщений, которые не были отправлены в TG')

    master_bot = MasterBot()

    for db_user in await DBUser.objects():
        await master_bot.send_user_updates(db_user)
