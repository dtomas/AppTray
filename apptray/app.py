import gtk

from rox import processes

from traylib import *
from traylib.pixbuf_helper import scale_pixbuf_to_size

import apptray.categories


default_icon_names = [
    'application-x-executable', 
    'mime-application:x-executable', 
    'gnome-mime-application-x-executable'
]


for icon_name in default_icon_names:
    icon_info = ICON_THEME.lookup_icon(icon_name, 22, 0)
    if icon_info:
        icon_path = icon_info.get_filename()
        try:
            default_icon = gtk.gdk.pixbuf_new_from_file(icon_path)
        except:
            continue
        break


class App:
    
    def __init__(self, handler):
        self.__handler = handler
        self.__icon = None

    def forget_icon(self):
        self.__icon = None

    def get_dnd_path(self):
        return ''

    def get_name(self):
        return ''
    
    def get_description(self):
        return ''

    def get_category(self):
        return "Unknown"
    
    def get_subcategory(self):
        return None

    def get_icon(self):
        if self.__icon:
            return self.__icon

        icon_path = self.icon_path
        if not icon_path:
            self.__icon = default_icon
        else:
            try:
                self.__icon = scale_pixbuf_to_size(
                    gtk.gdk.pixbuf_new_from_file(icon_path), 48
                )
            except:
                self.__icon = default_icon

        return self.__icon
    
    def get_icon_path(self):
        return None
    
    def get_command(self):
        return ()
    
    def get_help_command(self):
        return ()
    
    def get_versions_command(self):
        return ()
    
    def get_mime_types(self):
        return ()

    def run(self):
        processes.PipeThroughCommand(self.command, None, None).start()

    name = property(lambda self : self.get_name())
    description = property(lambda self : self.get_description())
    category = property(lambda self : self.get_category())
    subcategory = property(lambda self : self.get_subcategory())
    icon_path = property(lambda self : self.get_icon_path())
    icon = property(lambda self : self.get_icon())
    command = property(lambda self : self.get_command())
    help_command = property(lambda self : self.get_help_command())
    versions_command = property(lambda self : self.get_versions_command())
    dnd_path = property(lambda self : self.get_dnd_path())
    handler = property(lambda self : self.__handler)
    mime_types = property(lambda self : self.get_mime_types())
