import os
from cStringIO import StringIO

from rox import processes, file_monitor
from rox.basedir import xdg_data_dirs

from apptray.app_handler import AppHandler
from apptray.handlers.xdg.xdg_app import XdgApp, DesktopEntryNotShown


class XdgAppHandler(AppHandler):
    
    def __init__(self):
        AppHandler.__init__(self)

        self.__apps_dirs = []

        if not file_monitor.is_available():
            return

        for datadir in xdg_data_dirs:
            apps_dir = os.path.join(datadir, 'applications')
            if not os.path.isdir(apps_dir):
                continue
            file_monitor.watch(apps_dir, self.file_created, self.file_deleted)
            self.__apps_dirs.append(apps_dir)

    def init_apps(self):
        self.__desktop_files = {}
        
        for apps_dir in self.__apps_dirs:
            if not os.path.isdir(apps_dir):
                continue
            for leaf in os.listdir(apps_dir):
                path = os.path.join(apps_dir, leaf)
                if os.path.isdir(path):
                    continue
                if leaf in self.__desktop_files:
                    continue
                app_path = os.path.join(apps_dir, leaf)
                try:
                    app = XdgApp(self, app_path)
                except DesktopEntryNotShown:
                    continue
                else:
                    yield app
                    self.__desktop_files[leaf] = app

    def file_created(self, dir, leaf):
        # try to create a new app
        try:
            new_app = XdgApp(self, os.path.join(dir, leaf))
        except DesktopEntryNotShown:
            return
        # check if an app for this .desktop file is already there
        old_app = self.__desktop_files.get(leaf)
        if old_app:
            # check if the old app overrides the new one
            new_app_datadir = os.path.dirname(dir)
            old_app_datadir = os.path.dirname(os.path.dirname(old_app.path))
            for datadir in xdg_data_dirs:
                if datadir == new_app_datadir:
                    # the datadir of the new app overrules the one
                    # of the old one, so go on
                    break
                if datadir == old_app_datadir:
                    # the datadir of the old app overrules the one
                    # of the new one, so exit
                    return
            
            # remove the old app
            self.emit("app-removed", old_app)
            old_app.destroy()

        # add the new app
        self.emit("app-added", new_app, not old_app)
        
        self.__desktop_files[leaf] = new_app

    def file_deleted(self, dir, leaf):
        old_app = self.__desktop_files.get(leaf)
        if not old_app or os.path.dirname(old_app.path) != dir:
            return
        # remove the app
        self.__tray.remove_app(old_app)
        del self.__desktop_files[leaf]
        old_app.destroy()
        
        # look if the app is installed somewhere else
        for datadir in xdg_data_dirs:
            apps_dir = os.path.join(datadir, 'applications')
            path = os.path.join(apps_dir, leaf)
            if not os.path.exists(path) or os.path.isdir(path):
                continue
            # try to create a new app
            try:
                new_app = XdgApp(self, path)
            except DesktopEntryNotShown:
                continue
            # add the new app
            category_icon = self.emit("app-added", new_app, True)
            self.__desktop_files[leaf] = new_app

    def uninstall(self, app):
        s = StringIO()
        processes.PipeThroughCommand(
            ('dpkg', '--search', app.path), None, s
        ).wait()
        dpkg_search_str = s.getvalue()
        s.close()
        if not dpkg_search_str:
            return
        packages = dpkg_search_str.split(':')[0].split(',')
        other_apps = set()
        for package in packages:
            s = StringIO()
            processes.PipeThroughCommand(
                ('dpkg', '--listfiles', package), None, s
            ).wait()
            dpkg_list_str = s.getvalue()
            s.close()
            for other_app in self.__desktop_files.itervalues():
                if other_app is app:
                    continue
                if not isinstance(other_app, XdgApp):
                    continue
                if other_app.path in dpkg_list_str.splitlines():
                    other_apps.add(other_app)
        #print "Other apps: %s" % str(map(lambda a : a.name, other_apps))
        
