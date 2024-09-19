import asyncio
from typing import List

from telegram import Bot, Update
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, Application, MessageHandler, filters

from petTrackerBot.constants.paths import paths
from petTrackerBot.db_utils import DbUtils
from petTrackerBot.petTrackerApp.tables import DBUser
from petTrackerBot.tasks import restart_scheduler
from petTrackerBot.utils.WrappedHTTPXRequest import WrappedHTTPXRequest
from petTrackerBot.utils.app_state import APP_STATE
from petTrackerBot.utils.common import app_logger, Singleton
from petTrackerBot.constants.common import (
    TOKEN_BOT,
    DEBUG_MODE,
    WRITE_TIMEOUT,
)


class MasterBot(metaclass=Singleton):
    __application = None

    def __init__(self):
        self.bot = Bot(TOKEN_BOT, request=WrappedHTTPXRequest(write_timeout=WRITE_TIMEOUT))

    def run_application(self):
        self.__init_application()
        self.__application.run_polling(allowed_updates=Update.ALL_TYPES)

    def __init_application(self):
        self.__application = ApplicationBuilder() \
            .request(WrappedHTTPXRequest(write_timeout=WRITE_TIMEOUT)) \
            .token(TOKEN_BOT) \
            .concurrent_updates(True) \
            .post_init(self.post_init) \
            .build()

        # # # USERS # # #
        self.__application.add_handler(
            CommandHandler(
                command='start',
                callback=self.start
            )
        )

    @staticmethod
    async def post_init(application: Application):
        await DbUtils.create_db_tables()  # todo to async
        await restart_scheduler(application)

    async def start(self, update: Update, context):
        tg_user = update.effective_user
        if await DBUser.objects().where(DBUser.user_id == tg_user.id).first():
            await update.message.reply_text('Бот активен.\n'
                                            f'Запущен: {APP_STATE.FIRST_STARTED}.\n'
                                            f'Последний перезапуск: {APP_STATE.LAST_RESTARTED}')
            return

        await DBUser.insert(
            DBUser(
                user_id=tg_user.id,
                tg_data=tg_user.to_json(),
            )
        )

        await update.message.reply_text('Подписка на перемещение активирована.')
        # TODO Отправлять первый раз
        # TODO
        #   BACKLOG / Заполнять анкету для создания своего животного

    async def send_user_updates(self, db_user: DBUser):
        ...