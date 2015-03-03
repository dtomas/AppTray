import gtk, os, stat
from rox.AppInfo import AppInfo
from urlparse import urlsplit
from zeroinstall import SafeException
from zeroinstall.injector.iface_cache import iface_cache
from traylib import XDG_CONFIG_HOME
from apptray import PROJECT, SITE
from apptray.app import App
import apptray.categories

class ZeroApp(App):
    
    def __init__(self, handler, interface, category_id, app_dir):
        App.__init__(self, handler)
        self.__interface = interface
        self.__category_id = category_id
        self.__icon_path = None
        self.__app_dir = app_dir
        self.__appinfo = None

    def get_appinfo(self):
        if self.__appinfo == None:
            if not self.__app_dir:
                return None
            appinfo_path = os.path.join(self.__app_dir, 'AppInfo.xml')
            if not os.path.isfile(appinfo_path):
                return None
            self.__appinfo = AppInfo(appinfo_path)
        return self.__appinfo

    def get_name(self):
        return self.__interface.name

    def get_description(self):
        return self.__interface.summary
    
    def get_category(self):
        return self.__category_id

    def get_icon_path(self):
        if self.__icon_path:
            return self.__icon_path
        self.__icon_path = iface_cache.get_icon_path(self.__interface)
        if not self.__icon_path:
            return None
        return self.__icon_path

    def get_command(self):
        return ('0launch', self.__interface.uri)
    
    def get_versions_command(self):
        return ('0launch', '-gd', self.__interface.uri)
    
    def get_help_command(self):
        return ('0launch', 
                'http://rox.sourceforge.net/2005/interfaces/AddApp', 
                '--show-help', 
                self.__interface.uri)
        
    def get_mime_types(self):
        if not self.appinfo:
            return ()
        return self.appinfo.getCanRun()

    def get_dnd_path(self):
        i, host, i, i, i = urlsplit(self.__interface.uri)
        dnd_path = os.path.join(XDG_CONFIG_HOME, SITE, PROJECT, 
                                'Apps', host, self.name)
        self.__create_wrapper(dnd_path)
        return dnd_path

    def __create_wrapper(self, path):
        if os.path.isdir(path):
            return
        os.makedirs(path)
        if self.icon_path:
            os.symlink(self.icon_path, os.path.join(path, '.DirIcon'))
        apprun_path = os.path.join(path, 'AppRun')
        f = open(apprun_path, 'w')
        f.writelines(['#!/bin/sh\n', 
                      'if [ "$*" = "--versions" ]; then\n'
                      '  exec %s\n' % reduce(lambda s1,s2 : "".join((s1, " ", s2)), 
                                             self.versions_command),
                      'elif [ "$*" = "--help" ]; then\n',
                      '  exec %s\n' % reduce(lambda s1,s2 : "".join((s1, " ", s2)),
                                             self.help_command),
                      'else\n',
                      '  exec %s "$@"\n' % reduce(lambda s1,s2 : "".join((s1, " ", s2)),
                                             self.command),
                      'fi\n'])
        f.close()
        os.chmod(apprun_path, stat.S_IEXEC|stat.S_IREAD)
        if self.__category_id == "ROX-Applets":
            appletrun_path = os.path.join(path, 'AppletRun')
            f = open(appletrun_path, 'w')
            f.writelines(['#!/bin/sh\n', 
                          'exec 0launch --main="AppletRun" %s "$@"\n' % self.__interface.uri])
            f.close()
            os.chmod(appletrun_path, stat.S_IEXEC|stat.S_IREAD)
            
        appinfo = self.appinfo
        appmenu_lines = []
        if appinfo:
            for menu_item in appinfo.getAppMenu():
                #print menu_item
                icon = menu_item.get('icon')
                option = menu_item.get('option')
                label = menu_item.get('label')
                if not option or not label:
                    continue
                seq = ['    <Item option="%s" ' % option]
                if icon:
                    seq.append('icon="%s" ' % icon)
                seq.append(' label="%s" />\n' % label)
                appmenu_lines.append("".join(seq))

        appinfo_path = os.path.join(path, 'AppInfo.xml')
        f = open(appinfo_path, 'w')
        f.writelines(['<?xml version="1.0" ?>\n', 
                      '<AppInfo>\n', 
                      '  <Summary>%s</Summary>\n' % self.description,
                      '  <AppMenu>\n',
                      '    <Item option="--help" icon="gtk-help" label="%s" />\n' % _("Help"),
                      '    <Item option="--versions" label="%s" />\n' % _("Versions")] 
                      + appmenu_lines +
                      ['  </AppMenu>\n',
                      '</AppInfo>'])
        f.close()

    interface = property(lambda self : self.__interface)
    appinfo = property(get_appinfo)
