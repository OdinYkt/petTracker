import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List


class _Paths:
    _root = Path(__file__).parents[2]   # корневая папка запуска бота

    STATE_FILE_NAME = ".app_state"      # глобальное состояние

    @property
    def root(self) -> Path:
        return self._root

    @property
    def logs(self) -> Path:
        return self.root / '.logs'

    @property
    def temp(self) -> Path:
        return self.root / '.temp'

    @property
    def db_files(self) -> Path:
        return self.root / '.db_files'

    @property
    def state_file(self) -> Path:
        return self.root / self.STATE_FILE_NAME

    @property
    def database_folder(self) -> Path:
        return self.root / '.database'

    def _get_database(self, db_name: str) -> Path:
        if not self.database_folder.exists():
            self.database_folder.mkdir()
        return (self.database_folder / db_name).with_suffix('.db')

    @property
    def database(self) -> Path:
        return self._get_database('actual_db')

    @property
    def lock_restart(self) -> Path:
        return self.root / '.LOCK_RESTART'

    def get_new_log_file(self):
        if not self.logs.exists():
            self.logs.mkdir()
        return self.logs / f'parser_log_{datetime.now(timezone.utc).strftime("%d_%m_%Y_h%H_m%M_s%S")}.log'

    def get_last_logs(self, count: int) -> List[Path]:
        return sorted(self.logs.glob('*.log'), key=lambda x: x.stat().st_ctime, reverse=True)[:count]

    # TODO вынести функцию генерации папок
    def get_new_download_dir(self) -> Path:
        if not self.temp.exists():
            self.temp.mkdir()
        while True:
            folder_name = str(uuid.uuid4())
            folder_path = self.temp / folder_name
            if not folder_path.exists():
                folder_path.mkdir()
                return folder_path

    def get_new_db_files_folder(self) -> Path:
        if not self.db_files.exists():
            self.db_files.mkdir()
        while True:
            folder_name = str(uuid.uuid4())
            folder_path = self.db_files / folder_name
            if not folder_path.exists():
                folder_path.mkdir()
                return folder_path


paths = _Paths()
