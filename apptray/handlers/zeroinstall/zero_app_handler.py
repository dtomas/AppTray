import os

from rox import processes

from traylib import XDG_CONFIG_HOME, XDG_CACHE_HOME
from traylib import XDG_CACHE_HOME
from traylib import dir_monitor

from apptray import *
from apptray import categories
from apptray.app_handler import AppHandler
from apptray.handlers.zeroinstall.zero_app import ZeroApp

import zeroinstall
import zeroinstall.injector.iface_cache
from zeroinstall.injector.iface_cache import iface_cache
from zeroinstall.injector.autopolicy import AutoPolicy
from zeroinstall.injector.model import escape, unescape
from zeroinstall.zerostore import NotStored
from zeroinstall.injector.reader import InvalidInterface


class ZeroAppHandler(AppHandler):
    
    def __init__(self, tray):
        self.__tray = tray
        dir_monitor.add(os.path.join(XDG_CACHE_HOME, '0install.net', 'interfaces'), self)
        
    def handle_uri(self, uri):
        if not uri.startswith('http'):
            return
        processes.PipeThroughCommand(('0launch', '-gdr', uri), None, None).start()

    def add_apps(self):
        self.__apps = {}
        for uri in iface_cache.list_all_interfaces():
            self.__add(uri)
            yield None

    def uninstall(self, app):
        uri = app.interface.uri
        escaped_uri = escape(uri)
        try:
            os.remove(os.path.join(XDG_CACHE_HOME, 
                                '0install.net', 
                                'interfaces', 
                                escaped_uri))
        except OSError:
            pass
        try:
            os.remove(os.path.join(XDG_CONFIG_HOME, 
                                '0install.net',
                                'injector', 
                                'user_overrides', 
                                escaped_uri))
        except OSError:
            pass
        # remove all implementations
        policy = AutoPolicy(uri)
        policy.recalculate()
        for impl in policy.get_ranked_implementations(app.interface):
            try:
                path = policy.get_implementation_path(impl)
                if path and path.startswith(XDG_CACHE_HOME):
                    try:
                        os.removedirs(path)
                    except OSError:
                        pass
            except NotStored:
                pass

    def __add(self, uri, is_new = False):
        if not uri.startswith('http'):
            return
        try:
            interface = iface_cache.get_interface(uri)
        except InvalidInterface:
            return
        if interface.feed_for:
            return
        
        policy = AutoPolicy(interface.uri)
        policy.freshness = 0    # No further updates
        policy.recalculate()
        impl = policy.implementation[interface]
        
        if not impl:
            return
        
        # filter out libraries
        if hasattr(impl, 'main'):
            main = impl.main
        else:
            main = interface.main
        if not main:
            return

        # filter out applets
        if impl.id.startswith('.') or impl.id.startswith('/'):
            impl_path = impl.id
        elif impl.id.startswith('package:'):
            impl_path = None
        else:
            try:
                impl_path = policy.get_implementation_path(impl)
            except NotStored:
                return
        category_id = None
        if impl_path:
            applet_run = os.path.join(impl_path, os.path.dirname(main), 'AppletRun')
            if os.path.exists(applet_run):
                category_id = "ROX-Applets"

        if not category_id:
            category_id = "Unknown"
            for element in interface.metadata:
                if element.name == 'category' and element.content:
                    category_id = categories.get(element.content).id
                    break

        app_dir = os.path.join(impl_path, os.path.dirname(main))
        app_run = os.path.join(app_dir, 'AppRun')
        if not os.path.exists(app_run):
            app_dir = None
        app = ZeroApp(self, interface, category_id, app_dir)
        self.__tray.add_app(app, is_new)
        self.__apps[uri] = app
        if zeroinstall.version <= '0.31':
            policy.begin_icon_download(interface)
        else:
            policy.download_icon(interface)

    def file_created(self, dir, leaf):
        uri = unescape(leaf)
        if uri in self.__apps:
            return
        self.__add(uri, True)

    def file_deleted(self, dir, leaf):
        uri = unescape(leaf)
        app = self.__apps.get(uri)
        if not app:
            return
        self.__tray.remove_app(app)
        del self.__apps[uri]
