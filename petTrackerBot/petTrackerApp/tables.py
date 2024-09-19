from datetime import datetime

from piccolo.table import Table
from piccolo.columns import Timestamp, Varchar, JSON, Integer


class DBUser(Table):
    user_id = Integer()
    tg_data = JSON(null=True, default=dict())

    date_last_updated = Timestamp(null=True, default=None)
    date_register = Timestamp(default=datetime.now())


class DBMapInfo(Table):
    date_created = Timestamp(default=datetime.now())

    image_path = Varchar(length=2048)
    information = Varchar(length=4096)

