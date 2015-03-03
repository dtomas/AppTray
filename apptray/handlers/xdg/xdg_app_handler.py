import os
from rox import processes
from cStringIO import StringIO
from traylib import XDG_DATA_DIRS
from traylib import dir_monitor
from apptray.app_handler import AppHandler
from apptray.handlers.xdg.xdg_app import XdgApp, DesktopEntryNotShown


class XdgAppHandler(AppHandler):
    
    def __init__(self, tray):
        self.__tray = tray
        self.__apps_dirs = set()
        for datadir in XDG_DATA_DIRS:
            apps_dir = os.path.join(datadir, 'applications')
            if not os.path.isdir(apps_dir):
                continue
            dir_monitor.add(apps_dir, self)
            self.__apps_dirs.add(apps_dir)

    def add_apps(self):
        self.__desktop_files = {}
        
        for apps_dir in self.__apps_dirs:
            if not os.path.isdir(apps_dir):
                continue
            for leaf in os.listdir(apps_dir):
                yield None
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
                self.__desktop_files[leaf] = app
                self.__tray.add_app(app, False)

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
            for datadir in XDG_DATA_DIRS:
                if datadir == new_app_datadir:
                    # the datadir of the new app overrules the one of the old one, so go on
                    break
                if datadir == old_app_datadir:
                    # the datadir of the old app overrules the one of the new one, so exit
                    return
            
            # remove the old app
            self.__tray.remove_app(old_app)
            old_app.destroy()

        # add the new app
        self.__tray.add_app(new_app, not old_app)
        
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
        for datadir in XDG_DATA_DIRS:
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
            category_icon = self.__tray.add_app(new_app)
            self.__desktop_files[leaf] = new_app

    def uninstall(self, app):
        s = StringIO()
        processes.PipeThroughCommand(('dpkg', '--search', app.path), None, s).wait()
        dpkg_search_str = s.getvalue()
        s.close()
        if not dpkg_search_str:
            return
        packages = dpkg_search_str.split(':')[0].split(',')
        other_apps = set()
        for package in packages:
            s = StringIO()
            processes.PipeThroughCommand(('dpkg', '--listfiles', package), None, s).wait()
            dpkg_list_str = s.getvalue()
            s.close()
            for other_app in self.__tray.apps:
                if other_app == app:
                    continue
                if not isinstance(other_app, XdgApp):
                    continue
                if other_app.path in dpkg_list_str.splitlines():
                    other_apps.add(other_app)
        #print "Other apps: %s" % str(map(lambda a : a.name, other_apps))
        
