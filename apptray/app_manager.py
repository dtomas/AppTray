from apptray.app_handler import AppHandler


class AppManager(AppHandler):

    def __init__(self, handler_classes):
        AppHandler.__init__(self)
        self.__handler_classes = handler_classes
        self.__handlers = [
            handler_class() for handler_class in handler_classes
        ]
        for handler in self.__handlers:
            handler.connect(
                "app-added",
                lambda handler, app, is_new:
                    self.emit("app-added", app, is_new)
            )
            handler.connect(
                "app-removed",
                lambda handler, app: self.emit("app-removed", app)
            )

    def init_apps(self):
        for handler in self.__handlers:
            for app in handler.init_apps():
                yield app

    def handle_uri(self, uri):
        for handler in self.__handlers:
            if handler.handle_uri(uri):
                break
