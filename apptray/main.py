from functools import partial
from itertools import ifilter, imap
from operator import attrgetter

from rox.tasks import Task

from traylib.tray import Tray, TrayConfig
from traylib.icon import IconConfig
from traylib.managed_tray import ManagedTray

from apptray.app_manager import AppManager
from apptray.apptray_manager import manage_apptray
from apptray.main_icon import MainIcon
from apptray.search import AppSearchIndex

from apptray.handlers.xdg.xdg_app_handler import XdgAppHandler
from apptray.handlers.rox.rox_app_handler import RoxAppHandler


# Commented out for now, as it does not work with recent 0install API.
#try:
#    import zeroinstall
#except ImportError:
#    zeroinstall = None
#else:
#    from handlers.zeroinstall.zero_app_handler import ZeroAppHandler
#    _handler_classes.append(ZeroAppHandler)


class AppTray(ManagedTray):

    def __init__(self, icon_config, tray_config):
        search_index = AppSearchIndex()
        ManagedTray.__init__(
            self, icon_config, tray_config,
            managers=[
                partial(
                    manage_apptray,
                    icon_config=icon_config,
                    tray_config=tray_config,
                    app_manager=AppManager(
                        handler_classes=[XdgAppHandler, RoxAppHandler],
                    ),
                    search_index=search_index,
                ),
            ],
            create_menu_icon=partial(
                MainIcon,
                search_index=search_index,
            ),
        )
