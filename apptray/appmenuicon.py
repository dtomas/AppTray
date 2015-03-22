from operator import attrgetter

import gtk

from rox.tasks import Task

from traylib.icon import Icon

from apptray.app import App
from apptray.app_menu_item import AppMenuItem


class AppMenuIcon(Icon):

    def __init__(self, icon_config, category):
        Icon.__init__(self, icon_config)
        self.__category = category
        self.__apps = set()
        self.__current_app = None
        self.__menu = None
        self.__menu_right = None
        self.__new_apps = set()

    def icon_theme_changed(self):
        self.__menu = None
        self.__menu_right = None

    def add_app(self, app, is_new = True):
        if app in self.__apps:
            return
        self.__apps.add(app)
        if is_new:
            self.__new_apps.add(app)
            self.update_has_arrow()
        self.__menu = None
        self.__menu_right = None
        self.update_visibility()

    def remove_app(self, app):
        if app not in self.__apps:
            return
        self.__apps.remove(app)
        self.__menu = None
        self.__menu_right = None
        self.update_visibility()
        
    def remove_apps(self):
        self.__apps.clear()
        self.__menu = None
        self.__menu_right = None
        self.update_visibility()

    def __update_menu(self):
        menu = gtk.Menu()
        menu_right = gtk.Menu()
        apps = list(self.__apps)
        apps.sort(key=lambda x : x.name.lower())
        for app in apps:
            if app in self.__new_apps:
                icon_size = 48
            else:
                icon_size = 22
            menu.append(AppMenuItem(app, icon_size))
            menu_right.append(AppMenuItem(app, icon_size, submenu = True))

        self.__menu = menu    
        self.__menu_right = menu_right
        Task(self.__load_menu_icons((menu, menu_right)))

    def __load_menu_icons(self, menus):
        for menu in menus:
            if not menu:
                continue
            menu_items = list(menu.get_children())
            for menu_item in menu_items:
                menu_item.load_icon()
                yield None
            for menu_item in menu_items:
                menu_item.update_icon()
            menu.reposition()

    def get_menu_left(self):
        if not self.__menu:
            self.__update_menu()
        if self.__new_apps:
            self.__new_apps.clear()
            self.update_has_arrow()
            menu = self.__menu
            self.__menu = None
            return menu
        return self.__menu

    def get_menu_right(self):
        if not self.__menu_right:
            self.__update_menu()
        if self.__new_apps:
            self.__new_apps.clear()
            self.update_has_arrow()
            menu = self.__menu_right
            self.__menu_right = None
            return menu
        return self.__menu_right

    def get_dnd_uri(self):
        if self.__current_app and self.__entered:
            return self.__current_app.get_dnd_uri()
        return None

    def make_icon(self):
        return self.__category.find_icon(self.size)

    def make_tooltip(self):
        return self.__category.name

    def make_visibility(self):
        return bool(self.__apps)

    def make_has_arrow(self):
        return bool(self.__new_apps)
