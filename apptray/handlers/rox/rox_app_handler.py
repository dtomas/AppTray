import os

from traylib import APPDIRPATH

import rox
from rox import file_monitor

from apptray.app_handler import AppHandler
from apptray.handlers.rox.rox_app import RoxApp, NotAnAppDir


class RoxAppHandler(AppHandler):

    def __init__(self):
        AppHandler.__init__(self)
        self.__apps = {}
        self.__appsdir_watchers = {}
        self.__apprun_deleted_watchers = {}
        self.__appdir_deleted_watchers = {}
        self.__maybe_apprun_created_watchers = {}

    def _maybe_appdir_created(self, apps_dir, app_name):
        app_dir = os.path.join(apps_dir, app_name)
        if not rox.isappdir(app_dir):
            return
        self.__apps[app_dir] = app = RoxApp(self, app_dir)
        self.__apprun_deleted_watchers[app_dir] = file_monitor.watch(
            os.path.join(app_dir, 'AppRun'),
            on_file_deleted=self._apprun_deleted,
        )
        self.__appdir_deleted_watchers[app_dir] = file_monitor.watch(
            app_dir,
            on_file_deleted=self._appdir_deleted,
        )
        self.emit("app-added", app, True)

    def _maybe_appdir_deleted(self, apps_dir, app_name):
        app_dir = os.path.join(apps_dir, app_name)
        try:
            app = self.__apps.pop(app_dir)
        except KeyError:
            pass
        self.emit("app-removed", app)

    def _maybe_apprun_created(self, app_dir, leafname):
        if leafname != 'AppRun':
            return
        app_run = os.path.join(app_dir, 'AppRun')
        if not rox.isappdir(app_dir):
            return
        self.__apps[app_dir] = app = RoxApp(self, app_dir)
        file_monitor.unwatch(self.__maybe_apprun_created_watchers.pop(app_dir))
        self.__apprun_deleted_watchers[app_dir] = (
            file_monitor.watch(app_run, on_file_deleted=self._apprun_deleted)
        )
        self.__appdir_deleted_watchers[app_dir] = (
            file_monitor.watch(app_dir, on_file_deleted=self._appdir_deleted)
        )
        self.emit("app-added", app, True)

    def _apprun_deleted(self, app_run):
        app_dir = os.path.dirname(app_run)
        self.emit("app-removed", self.__apps.pop(app_dir))
        #file_monitor.unwatch(self.__appdir_deleted_watchers.pop(app_dir))
        file_monitor.unwatch(self.__apprun_deleted_watchers.pop(app_dir))
        self.__maybe_apprun_created_watchers[app_dir] = file_monitor.watch(
            app_dir, on_child_created=self._maybe_apprun_created,
        )

    def _appdir_deleted(self, app_dir):
        self.emit("app-removed", self.__apps.pop(app_dir))
        file_monitor.unwatch(self.__appdir_deleted_watchers.pop(app_dir))
        file_monitor.unwatch(self.__apprun_deleted_watchers.pop(app_dir))

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

                if not file_monitor.is_available():
                    return
                self.__apprun_deleted_watchers[app_path] = file_monitor.watch(
                    os.path.join(app_path, 'AppRun'),
                    on_file_deleted=self._apprun_deleted,
                )
                self.__appdir_deleted_watchers[app_path] = file_monitor.watch(
                    app_path,
                    on_file_deleted=self._appdir_deleted,
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
            #self._monitor_apps_dir(apps_dir)
            self.__appsdir_watchers[apps_dir] = file_monitor.watch(
                apps_dir,
                on_child_created=self._maybe_appdir_created,
            )
