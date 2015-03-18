from itertools import ifilter, imap
from operator import attrgetter

from rox.tasks import Task

from traylib import *
from traylib.tray import Tray, TrayConfig
from traylib.icon import IconConfig

from apptray.appmenuicon import AppMenuIcon
from apptray.categories import categories
from apptray.main_icon import MainIcon
from apptray.sendto_handler import SendToHandler
from apptray.search import AppSearchIndex

from apptray.handlers.xdg.xdg_app_handler import XdgAppHandler
from apptray.handlers.rox.rox_app_handler import RoxAppHandler


_handler_classes = [XdgAppHandler, RoxAppHandler]


# Commented out for now, as it does not work with recent 0install API.
#try:
#    import zeroinstall
#except ImportError:
#    zeroinstall = None
#else:
#    from handlers.zeroinstall.zero_app_handler import ZeroAppHandler
#    _handler_classes.append(ZeroAppHandler)


class AppTray(Tray):

    def __init__(self, icon_config, tray_config):
        Tray.__init__(self, icon_config, tray_config, MainIcon)

        self.__apps = set()

        self.add_box("Categories")

        self.__search_index = AppSearchIndex()
        #self.__sendto_handler = SendToHandler()

        self.__handlers = set()

        category_objs = categories
        for category in category_objs:
            category_icon = AppMenuIcon(icon_config, category)
            self.add_icon("Categories", category.id, category_icon)

        def add_apps():
            for handler_class in _handler_classes:
                handler = handler_class(
                    app_added=self.add_app,
                    app_removed=self.remove_app,
                )
                self.__handlers.add(handler)
                for app in handler:
                    self.add_app(app, False)
                    yield None
        Task(add_apps())

        #self.add_box("Actions", separator = True)
        #self.add_icon("Actions", "MainIcon", MainIcon(self))
        
        self.update()

    def update_option_menus(self):
        Tray.update_option_menus(self)
        if self.has_box("search-result"):
            self.remove_box("search-result")
        self.add_box("search-result", side=self.tray_config.menus)

    def get_custom_menu_items(self):
        menu_item = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        menu_item.connect("activate", self.__refresh)
        return [menu_item]

    def __refresh(self, menu_item):
        for category in categories:
            icon = self.get_icon(category.id)
            icon.remove_apps()
        for handler in self.__handlers:
            Task(handler.add_apps())

    def add_app(self, app, is_new = True):
        self.get_icon(app.category).add_app(app, is_new)
        self.__search_index.add_app(app)
        #self.__sendto_handler.app_added(app)
        self.__apps.add(app)

    def remove_app(self, app):
        self.get_icon(app.category).remove_app(app)
        self.__search_index.remove_app(app)
        #self.__sendto_handler.app_removed(app)
        self.__apps.remove(app)

    def update(self):
        for icon in self.icons:
            icon.update_icon()
            icon.update_visibility()
            icon.update_tooltip()
            icon.update_has_arrow()
            icon.update_is_drop_target()

    handlers = property(lambda self : self.__handlers)
    apps = property(lambda self : self.__apps)
    search_index = property(lambda self : self.__search_index)
