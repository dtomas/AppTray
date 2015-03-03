import gtk, rox, os
from traylib import ICON_THEME


class Category:

    def __init__(self, pos, id, name, icon_names):
        self.__pos = pos
        self.__id = id
        self.__name = name
        self.__icon_names = icon_names

    def find_icon(self, size):
        icon_path = None
        for icon_name in self.__icon_names:
            icon_info = ICON_THEME.lookup_icon(icon_name, size, 0)
            if icon_info:
                icon_path = icon_info.get_filename()
                break
        assert icon_path
        return gtk.gdk.pixbuf_new_from_file(icon_path)

    pos = property(lambda self : self.__pos)
    id = property(lambda self : self.__id)
    name = property(lambda self : self.__name)
