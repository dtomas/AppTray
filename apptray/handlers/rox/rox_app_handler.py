import os

from traylib import APPDIRPATH

from rox import file_monitor

from apptray.app_handler import AppHandler
from apptray.handlers.rox.rox_app import RoxApp, NotAnAppDir


class RoxAppHandler(AppHandler):

    def __init__(self):
        AppHandler.__init__(self)
        self.__apps = {}

    def _monitor_apps_dir(self, apps_dir):
        file_monitor.watch(apps_dir, self.file_created, self.file_deleted)
        # FIXME: Wanna watch subdirectories, but this makes the dir monitor hang
        # when there are many of them. Is this some gamin/inotify limitation?
        #for dirname in os.listdir(apps_dir):
        #    path = os.path.join(apps_dir, dirname)
        #    if not os.path.isdir(path):
        #        continue
        #    if path in self.__apps:
        #        continue
        #    #self._monitor_apps_dir(path)

    def _get_apps(self, apps_dir):
        for app_dir in os.listdir(apps_dir):
            app_path = os.path.join(apps_dir, app_dir)
            if not os.path.isdir(app_path):
                continue
            try:
                app = RoxApp(self, app_path)
            except NotAnAppDir:
                # Not an app dir, recurse...
                for app in self._get_apps(app_path):
                    yield app
            else:
                self.__apps[app_path] = app
                yield app
                file_monitor.watch(
                    app_path, self.file_created, self.file_deleted
                )

    def init_apps(self):
        for apps_dir in APPDIRPATH:
            if not os.path.isdir(apps_dir):
                continue
            for app in self._get_apps(apps_dir):
                yield app

        if not file_monitor.is_available():
            return

        for apps_dir in APPDIRPATH:
            if not os.path.isdir(apps_dir):
                continue
            self._monitor_apps_dir(apps_dir)

    def file_created(self, dir, leaf):
        path = os.path.join(dir, leaf)
        if leaf == 'AppRun':
            if os.access(path, os.X_OK):
                # A regular dir is turned into an app dir.
                path = dir
        elif not os.path.isdir(path):
            return
        try:
            app = RoxApp(self, path)
        except NotAnAppDir:
            pass
        else:
            self.__apps[path] = app
            self.emit("app-added", app)
        file_monitor.watch(path, self.file_created, self.file_deleted)

    def file_deleted(self, dir, leaf):
        path = os.path.join(dir, leaf)
        if leaf == 'AppRun':
            # An app dir is turned into a regular dir.
            path = dir
        elif not os.path.isdir(path):
            return
        try:
            app = self.__apps[path]
        except KeyError:
            return
        self.emit("app-removed", app)
