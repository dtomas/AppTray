import os
import xml.etree.ElementTree as ET 

from apptray.app import App


class NotAnAppDir(Exception):
    """
    Raised when trying to create a RoxApp from a directory which is not
    an app dir.
    """


class RoxApp(App):

    def __init__(self, handler, app_dir):
        App.__init__(self, handler)
        self.__app_dir = app_dir
        self.__app_run = os.path.join(app_dir, "AppRun")
        if not os.access(self.__app_run, os.X_OK):
            raise NotAnAppDir(app_dir)

        self.__dir_icon = os.path.join(app_dir, ".DirIcon")
        if not os.access(self.__app_dir, os.R_OK):
            self.__dir_icon = None

        self.__help_dir = os.path.join(app_dir, "Help")
        if not os.path.isdir(self.__help_dir):
            self.__help_dir = None

        self.__description = None
        self.__mime_types = []

        self.__app_info = os.path.join(app_dir, "AppInfo.xml")
        if os.access(self.__app_dir, os.R_OK):
            tree = ET.parse(self.__app_info)

            elem = tree.find("Summary")
            if elem is None:
                elem = tree.find("About/Purpose")
            if elem is not None:
                self.__description = elem.text

            for elem in tree.findall("CanRun/MimeType"):
                mime_type = elem.get('type')
                if not mime_type:
                    continue
                self.__mime_types.append(mime_type)

    def get_name(self):
        return os.path.basename(self.__app_dir)

    def get_description(self):
        return self.__description

    def get_command(self):
        return [self.__app_run]

    def get_dnd_path(self):
        return self.__app_dir

    def get_icon_path(self):
        return self.__dir_icon

    def get_mime_types(self):
        return self.__mime_types
    
    def get_help_command(self):
        if not self.__help_dir:
            return ()
        return ('rox', self.__help_dir)
