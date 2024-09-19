from piccolo.conf.apps import AppRegistry
from piccolo.engine.sqlite import SQLiteEngine

from petTrackerBot.constants.paths import paths

DB = SQLiteEngine(
    path=paths.database,
    check_same_thread=False
)

# A list of paths to piccolo apps
# e.g. ['blog.piccolo_app']
APP_REGISTRY = AppRegistry(apps=['petTrackerBot.petTrackerApp.piccolo_app'])
