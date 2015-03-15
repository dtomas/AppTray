from traylib import *
from traylib.icon import Icon


class AppIcon(Icon):

    def __init__(self, app, icon_config):
        Icon.__init__(self, icon_config)

        self.__app = app

        self.drag_source_set(
            gtk.gdk.BUTTON1_MASK, [("text/uri-list", 0, TARGET_URI_LIST)],
            gtk.gdk.ACTION_COPY
        )
        self.connect("drag-data-get", self.__drag_data_get)

        self.update_tooltip()
        self.update_icon()
        self.update_visibility()

    def __drag_data_get(self, widget, context, data, info, time):
        data.set_uris([self.__app.dnd_path])

    def make_visibility(self):
        return True

    def make_tooltip(self):
        return self.__app.name

    def get_icon_pixbuf(self):
        return self.__app.icon

    def click(self, time):
        self.__app.run()
