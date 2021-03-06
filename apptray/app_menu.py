import gtk

import rox
from rox import processes


class AppMenu(gtk.Menu):

    def __init__(self, app):
        gtk.Menu.__init__(self)
        self.__app = app
        menu_item = gtk.ImageMenuItem(gtk.STOCK_HELP)
        menu_item.connect("activate", lambda menu_item: app.show_help())
        self.append(menu_item)
        if not app.has_help():
            menu_item.set_sensitive(False)
        #menu_item = gtk.ImageMenuItem(_("Versions"))
        #menu_item.connect("activate", self.__activate, app.versions_command)
        #self.append(menu_item)
        #if not app.versions_command:
        #    menu_item.set_sensitive(False)
        self.append(gtk.SeparatorMenuItem())
        menu_item = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        menu_item.connect("activate", lambda menu_item: app.run())
        self.append(menu_item)
        #self.append(gtk.SeparatorMenuItem())
        #menu_item = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        #menu_item.connect("activate", self.__uninstall)
        #self.append(menu_item)
        #if not hasattr(app.handler, 'uninstall'):
        #    menu_item.set_sensitive(False)

    def __uninstall(self, menu_item):
        if rox.confirm(
                _("Really delete the application \"%s\"?" % self.__app.name), 
                gtk.STOCK_DELETE):
            self.__app.handler.uninstall(self.__app)
