import gobject

from apptray.app import App


class AppHandler(gobject.GObject):

    def init_apps(self):
        """
        Get all available applications.

        @return: iterator of L{apptray.app.App}
            The initial applications.
        """
        raise NotImplementedError

    def handle_uri(self, uri):
        """Handle a URI dragged to the main icon."""


gobject.type_register(AppHandler)
gobject.signal_new(
    "app-added", AppHandler, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    (object, bool)
)
gobject.signal_new(
    "app-removed", AppHandler, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    (object,)
)
