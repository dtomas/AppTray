import os

from traylib import XDG_CONFIG_HOME

_sendto_dir = os.path.join(XDG_CONFIG_HOME, 'rox.sourceforge.net', 'SendTo')
_runactions_dir = os.path.join(
    XDG_CONFIG_HOME, 'rox.sourceforge.net', 'MIME-types'
)

if not os.path.exists(_sendto_dir):
    os.makedirs(_sendto_dir)

if not os.path.exists(_runactions_dir):
    os.makedirs(_runactions_dir)

class SendToItemNotCreated(Exception):
    pass


class SendToItem:
    
    def __init__(self, app, mime_type):
        assert mime_type
        filename = mime_type.replace('/', '_')
        sendto_dir = os.path.join(_sendto_dir, '.%s' % filename)
        if not os.path.isdir(sendto_dir):
            try:
                os.makedirs(sendto_dir)
            except OSError:
                raise SendToItemNotCreated

        self.__path = os.path.join(sendto_dir, app.name)
        try:
            os.symlink(app.dnd_path, self.__path)
        except OSError:
            raise SendToItemNotCreated

        runaction_path = os.path.join(_runactions_dir, filename)
        if not os.path.exists(runaction_path):
            os.symlink(self.__path, runaction_path)

    def remove(self):
        os.remove(self.__path)
