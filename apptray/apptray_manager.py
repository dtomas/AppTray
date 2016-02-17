from apptray.categories import categories
from apptray.appmenuicon import AppMenuIcon
from apptray.app_manager import AppManager


def manage_apptray(tray, icon_config, tray_config, app_manager, search_index):

    tray.add_box("Categories")

    app_manager_handlers = []
    tray_config_handlers = []

    def menus_changed(tray_config):
        tray.remove_box("search-result")
        tray.add_box("search-result", side=tray_config.menus)

    tray.add_box("search-result", side=tray_config.menus)

    def app_added(manager, app, is_new=True):
        tray.get_icon(app.category).add_app(app, is_new)
        search_index.add_app(app)

    def app_removed(manager, app):
        tray.get_icon(app.category).remove_app(app)
        search_index.remove_app(app)

    def manage():
        tray_config_handlers.append(
            tray_config.connect("menus-changed", menus_changed)
        )
        app_manager_handlers.append(
            app_manager.connect("app-added", app_added)
        )
        app_manager_handlers.append(
            app_manager.connect("app-removed", app_removed)
        )

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
        for handler in app_manager_handlers:
            app_manager.disconnect(handler)
        for handler in tray_config_handlers:
            tray_config.disconnect(handler)
        for category in categories:
            tray.remove_icon(category.id)
            yield None
        search_index.clear()

    return manage, unmanage
