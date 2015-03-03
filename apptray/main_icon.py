from traylib import *
from traylib.menu_icon import MenuIcon


class MainIcon(MenuIcon):

    def get_icon_names(self):
        return ["system-installer"]

    def make_is_drop_target(self):
        return True
    
    def make_tooltip(self):
        if self.icon_config.hidden:
            s = _("Click or scroll up to show application menus.\n")
        else:
            s = _("Click or scroll down to hide the application menus.\n")
        s += _("Drop a 0install-link to add an application.")
        #s += _("Right click will open the AppTray menu.")
        return s

    def uris_dropped(self, uris, action):
        for uri in uris:
            for handler in self.tray.handlers:
                handler.handle_uri(uri)
