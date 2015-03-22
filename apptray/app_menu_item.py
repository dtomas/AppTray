import gtk

from rox.tasks import Task

from traylib import TOOLTIPS, TARGET_URI_LIST
from traylib.pixbuf_helper import scale_pixbuf_to_size

from apptray.app_menu import AppMenu


class AppMenuItem(gtk.ImageMenuItem):
    
    def __init__(self, app, icon_size, submenu = False):
        gtk.ImageMenuItem.__init__(self, app.name)
        self.__app = app
        self.__icon_size = icon_size

        if app.description and not submenu:
            TOOLTIPS.set_tip(self, app.description)
        self.set_size_request(-1, icon_size + 4)

        self.drag_source_set(gtk.gdk.BUTTON1_MASK, 
                    [("text/uri-list", 0, TARGET_URI_LIST)], 
                    gtk.gdk.ACTION_ASK|gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE)
        self.connect("drag-data-get", self.__drag_data_get)
        self.connect("drag-begin", self.__drag_begin)
        
        if submenu:
            self.set_submenu(AppMenu(app))
        else:
            self.connect("activate", self.__signal_activate)
            #self.connect("button-press-event", self.__button_press_event)
            
    #def __button_press_event(self, widget, event):
    #    if event.button != 3:
    #        return
    #    menu = AppMenu(self.__app)
    #    menu.show_all()
    #    menu.popup(None, self, None, event.button, event.time)
    
    def load_icon(self):
        self.__app.icon
        
    def update_icon(self):
        if self.__app.icon:
            pixbuf = scale_pixbuf_to_size(
                self.__app.icon, self.__icon_size, scale_up = True
            )
            self.get_image().set_from_pixbuf(pixbuf)

    def __drag_data_get(self, widget, drag_context, selection_data, info,
                        timestamp):
        selection_data.set_uris(['file://' + self.__app.dnd_path])

    def __drag_begin(self, widget, drag_context):
        icon = self.__app.icon
        if icon:
            self.drag_source_set_icon_pixbuf(scale_pixbuf_to_size(icon, 48))        

    def __signal_activate(self, widget):
        self.__app.run()
