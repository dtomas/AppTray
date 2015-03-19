from traylib import *
from traylib.menu_icon import MenuIcon
from traylib.icon_config import IconConfig

from apptray.search import AppSearchDialog


class MainIcon(MenuIcon):
    __search_dialog = None

    def get_icon_names(self):
        return ["system-installer"]

    def make_is_drop_target(self):
        return True
    
    def make_tooltip(self):
        parts = []
        if self.icon_config.hidden:
            parts.append(_("Scroll up to show application menus."))
        else:
            parts.append(_("Scroll down to hide the application menus."))
        parts += [
            _("Click to find an application."),
            #_("Drop a 0install-link to add an application."),
        ]
        #s += _("Right click will open the AppTray menu.")
        return '\n'.join(parts)

    def get_custom_menu_items(self):
        menu_item = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        menu_item.connect("activate", lambda menu_item: self.tray.refresh)
        return [menu_item]

    def click(self, time):
        if self.__search_dialog is None:
            self.__search_dialog = AppSearchDialog(
                self.tray,
                IconConfig(
                    size=self.tray.icon_config.size,
                    edge=self.tray.icon_config.edge,
                    effects=self.tray.icon_config.effects,
                    pos_func=self.tray.icon_config.pos_func,
                    hidden=False,
                ),
            )

            def unrealized(search_dialog):
                self.tray.clear_box("search-result")
                self.__search_dialog = None

            self.__search_dialog.connect("unrealize", unrealized)
        else:
            self.__search_dialog.destroy()

    def uris_dropped(self, uris, action):
        for uri in uris:
            for handler in self.tray.handlers:
                handler.handle_uri(uri)
