import os
from traylib import XDG_CONFIG_HOME

_sendto_dir = os.path.join(XDG_CONFIG_HOME, 'rox.sourceforge.net', 'SendTo')

if not os.path.isdir(_sendto_dir):
    os.makedirs(_sendto_dir)

class SendToItemNotCreated(Exception):
    pass


class SendToItem:
    
    def __init__(self, app, mime_type):
        assert mime_type
        sendto_dir = os.path.join(_sendto_dir, '.%s' % mime_type.replace('/', '_'))
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

    def remove(self):
        os.remove(self.__path)
