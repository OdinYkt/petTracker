from piccolo.table import create_db_tables

from petTrackerBot.petTrackerApp.tables import DBUser, DBMapInfo
from petTrackerBot.utils.common import app_logger


class DbUtils:
    """Единый доступ ко всем функциям работы с базой данных"""
    __TABLES_CREATED = False

    @staticmethod
    async def create_db_tables():
        if DbUtils.__TABLES_CREATED:
            return
        await create_db_tables(DBUser, DBMapInfo, if_not_exists=True)
        DbUtils.__TABLES_CREATED = True
