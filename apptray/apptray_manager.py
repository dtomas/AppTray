from traylib.icon_manager import IconManager

from apptray.categories import categories
from apptray.appmenuicon import AppMenuIcon
from apptray.app_manager import AppManager


def manage_apptray(tray, icon_config, tray_config, app_manager, search_index):

    tray.add_box("Categories")

    class TrayConfigurable(object):

        def update_option_menus(self):
            if tray.has_box("search-result"):
                tray.remove_box("search-result")
            tray.add_box("search-result", side=tray_config.menus)

    tray_configurable = TrayConfigurable()
    tray_config.add_configurable(tray_configurable)
    tray_configurable.update_option_menus()

    def app_added(manager, app, is_new=True):
        tray.get_icon(app.category).add_app(app, is_new)
        search_index.add_app(app)

    def app_removed(manager, app):
        tray.get_icon(app.category).remove_app(app)
        search_index.remove_app(app)

    app_added_handler = app_manager.connect("app-added", app_added)
    app_removed_handler = app_manager.connect("app-removed", app_removed)

    def manage():
        for category in categories:
            category_icon = AppMenuIcon(icon_config, category)
            tray.add_icon("Categories", category.id, category_icon)
            yield None

        for app in app_manager.init_apps():
            app_added(app_manager, app, False)
            yield None

        for icon in tray.icons:
            icon.update_icon()
            icon.update_visibility()
            icon.update_tooltip()
            icon.update_has_arrow()
            icon.update_is_drop_target()
            yield None

    def unmanage():
        app_manager.disconnect(app_added_handler)
        app_manager.disconnect(app_removed_handler)
        for category in categories:
            tray.remove_icon(category.id)
            yield None
        search_index.clear()

    return manage, unmanage
