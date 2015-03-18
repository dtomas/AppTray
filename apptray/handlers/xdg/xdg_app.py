import re
import os
from ConfigParser import RawConfigParser, NoOptionError

import gtk

from rox import i18n
from rox.basedir import xdg_data_dirs

from traylib import *

from apptray import categories
from apptray.app import App


class DesktopEntryNotShown(Exception):
    pass

SECTION_DESKTOP_ENTRY = "Desktop Entry"


class XdgApp(App):

    def __init__(self, handler, path):
        App.__init__(self, handler)
        self.__path = path

        parser = RawConfigParser()
        
        if parser.read(path) != [path]:
            raise DesktopEntryNotShown()
        
        if not parser.has_section(SECTION_DESKTOP_ENTRY):
            raise DesktopEntryNotShown()

        if not parser.has_option(SECTION_DESKTOP_ENTRY, "Exec"):
            raise DesktopEntryNotShown()

        try:
            if parser.get(SECTION_DESKTOP_ENTRY, "Type") != "Application":
                raise DesktopEntryNotShown()
        except NoOptionError:
            raise DesktopEntryNotShown()

        languages = i18n.expand_languages()
        
        self.__name = None
        for lang in languages:
            try:
                self.__name = parser.get(
                    SECTION_DESKTOP_ENTRY, "Name[%s]" % lang
                )
                break
            except NoOptionError:
                pass
        if not self.__name:
            try:
                self.__name = parser.get(SECTION_DESKTOP_ENTRY, "Name")
            except NoOptionError:
                raise DesktopEntryNotShown()
        if not self.__name:
            for lang in languages:
                try:
                    self.__name = parser.get(
                        SECTION_DESKTOP_ENTRY, "GenericName[%s]" % lang
                    )
                    break
                except NoOptionError:
                    pass
        if not self.__name:
            try:
                self.__name = parser.get(SECTION_DESKTOP_ENTRY, "GenericName")
            except NoOptionError:
                raise DesktopEntryNotShown()

        try:
            if parser.get(SECTION_DESKTOP_ENTRY, "Hidden") == "true":
                raise DesktopEntryNotShown()
        except NoOptionError:
            pass

        try:
            if parser.get(SECTION_DESKTOP_ENTRY, "NoDisplay") == "true":
                raise DesktopEntryNotShown()
        except NoOptionError:
            pass

        desktop_session = os.getenv('DESKTOP_SESSION')

        if desktop_session:
            try:
                only_show_in = parser.get(SECTION_DESKTOP_ENTRY, "OnlyShowIn")
            except NoOptionError:
                pass
            else:
                if desktop_session not in only_show_in.split(';'):
                    raise DesktopEntryNotShown()
            try:
                not_show_in = parser.get(SECTION_DESKTOP_ENTRY, "NotShowIn")
            except NoOptionError:
                pass
            else:
                if desktop_session in not_show_in.split(';'):
                    raise DesktopEntryNotShown()

        try:
            self.__exe = parser.get(SECTION_DESKTOP_ENTRY, "Exec")
        except NoOptionError:
            raise DesktopEntryNotShown()

        self.__command = re.sub('%[FfuUdDnNickvm]', '', self.__exe).split()

        self.__description = None
        for lang in languages:
            try:
                self.__description = parser.get(
                    SECTION_DESKTOP_ENTRY, "Comment[%s]" % lang
                )
                break
            except NoOptionError:
                pass
        if not self.__description:
            try:
                self.__description = parser.get(
                    SECTION_DESKTOP_ENTRY, "Comment"
                )
            except NoOptionError:
                pass
        if not self.__description:
            for lang in languages:
                try:
                    self.__description = parser.get(
                        SECTION_DESKTOP_ENTRY, "GenericName[%s]" % lang
                    )
                    break
                except NoOptionError:
                    pass
        if not self.__description:
            try:
                self.__description = parser.get(
                    SECTION_DESKTOP_ENTRY, "GenericName"
                )
            except NoOptionError:
                raise DesktopEntryNotShown()
        if not self.__description:
            self.__description = self.__name

        try:
            self.__icon_name_or_path = parser.get(
                SECTION_DESKTOP_ENTRY, "Icon"
            )
            
            # fix for .desktop files containing an icon name with extension
            if not os.path.isabs(self.__icon_name_or_path):
                if (self.__icon_name_or_path.endswith('.png') 
                        or self.__icon_name_or_path.endswith('.svg')
                        or self.__icon_name_or_path.endswith('.xpm')):
                    self.__icon_name_or_path = self.__icon_name_or_path[
                        :len(self.__icon_name_or_path)-4
                    ]
        except NoOptionError:
            self.__icon_name_or_path = ''

        self.__category = "Unknown"
        try:
            cats = parser.get(SECTION_DESKTOP_ENTRY, "Categories").split(';')
            self.__category = categories.get(*cats).id
        except NoOptionError:
            pass

        try:
            mime_types = parser.get(SECTION_DESKTOP_ENTRY, "MimeType")
            self.__mime_types = mime_types.split(';')
        except NoOptionError:
            self.__mime_types = ()

        self.__icon_theme_changed_handler = ICON_THEME.connect(
            "changed", self.__icon_theme_changed
        )

        app_name = os.path.basename(path)
        app_name = app_name[0:len(app_name)-8]
        self.__doc_dir = None
        for data_dir in xdg_data_dirs:
            doc_dir = os.path.join(data_dir, 'doc', app_name)
            if os.path.isdir(doc_dir):
                self.__doc_dir = doc_dir
                break

        self.__name = unicode(self.__name)
        self.__description = unicode(self.__description)

        assert self.__command
        assert self.__name
        assert self.__category
        assert self.__description
        assert hasattr(self, '_XdgApp__icon_name_or_path')

    def __icon_theme_changed(self, theme):
        if not os.path.isabs(self.__icon_name_or_path):
            self.forget_icon()

    def destroy(self):
        ICON_THEME.disconnect(self.__icon_theme_changed_handler)

    def get_name(self):
        return self.__name
    
    def get_description(self):
        return self.__description
    
    def get_category(self):
        return self.__category

    def get_icon_path(self):
        if not self.__icon_name_or_path:
            return None
        if not os.path.isabs(self.__icon_name_or_path):
            icon_info = ICON_THEME.lookup_icon(self.__icon_name_or_path, 22, 0)
            if icon_info:
                return icon_info.get_filename()
        else:
            return self.__icon_name_or_path
        return None

    def get_command(self):
        return self.__command
    
    def get_help_command(self):
        if not self.__doc_dir:
            return ()
        return ('rox', self.__doc_dir)

    def get_dnd_path(self):
        return self.__path
    
    def get_mime_types(self):
        return self.__mime_types

    exe = property(lambda self : self.__exe)
    path = property(lambda self : self.__path)
