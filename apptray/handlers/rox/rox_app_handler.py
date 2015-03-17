import os

from apptray.app_handler import AppHandler
from apptray.handlers.rox.rox_app import RoxApp, NotAnAppDir


class RoxAppHandler(AppHandler):

    def __init__(self, app_added, app_removed):
        self.__app_added = app_added
        self.__app_removed = app_removed

        appdirpath = os.getenv('APPDIRPATH')
        if not appdirpath:
            self.__apps_dirs = [os.path.expanduser(os.path.join('~', 'Apps'))]
        else:
            self.__apps_dirs = appdirpath.split(os.pathsep)

    def _get_apps(self, apps_dir):
        for app_dir in os.listdir(apps_dir):
            app_path = os.path.join(apps_dir, app_dir)
            if not os.path.isdir(app_path):
                continue
            try:
                yield RoxApp(self, app_path)
            except NotAnAppDir:
                # Not an app dir, recurse...
                for app in self._get_apps(app_path):
                    yield app

    def __iter__(self):
        for apps_dir in self.__apps_dirs:
            for app in self._get_apps(apps_dir):
                yield app
