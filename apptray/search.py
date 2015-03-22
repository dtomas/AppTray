import sqlite3

import gtk

from apptray.appicon import AppIcon


class AppSearchIndex(object):

    def __init__(self):
        self.__apps = {}
        self.__conn = sqlite3.connect(":memory:")
        self.__conn.execute(
            'CREATE TABLE apps '
                '(hash INTEGER PRIMARY KEY, '
                'name VARCHAR(16), '
                'command VARCHAR(16), '
                'description VARCHAR(64))'
        )
        self.__conn.execute('CREATE INDEX name_index ON apps (name)')
        self.__conn.execute('CREATE INDEX command_index ON apps (command)')
        self.__conn.execute(
            'CREATE INDEX description_index ON apps (description)'
        )

    def add_app(self, app):
        self.__conn.execute(
            'INSERT INTO apps VALUES (?, ?, ?, ?)',
            (hash(app), app.name, ' '.join(app.command), app.description)
        )
        self.__apps[hash(app)] = app

    def remove_app(self, app):
        app_hash = hash(app)
        del self.__apps[app_hash]
        self.__conn.execute(
            'DELETE FROM apps WHERE hash = ?', (app_hash,)
        )

    def clear(self):
        self.__conn.execute('DELETE FROM apps')
        self.__apps.clear()

    def search(self, keywords, on_result, on_finish):
        c = self.__conn.cursor()
        parts = ['SELECT hash FROM apps WHERE']
        conditions = []
        args = ()
        for keyword in keywords:
            keyword = '%%%s%%' % keyword
            conditions.append(
                '(name LIKE ? OR command LIKE ? OR description LIKE ?)'
            )
            args += (keyword, keyword, keyword)
        parts.append(' AND '.join(conditions))
        c.execute(' '.join(parts), args)
        for result in c.fetchall():
            on_result(self.__apps[result[0]])
        on_finish()


class AppSearchDialog(gtk.Window):

    def __init__(self, tray, icon_config, search_index):
        gtk.Window.__init__(self)

        self.__tray = tray

        frame = gtk.Frame(_("Find applications"))
        self.add(frame)

        box = gtk.HBox()
        frame.add(box)

        self.__search_entry = gtk.Entry()

        box.pack_start(self.__search_entry)

        self.set_decorated(False)

        if icon_config.pos_func is not None:
            x, y, __ = icon_config.pos_func(self)
            self.move(x, y)
        else:
            self.set_position(gtk.WIN_POS_MOUSE)

        self.show_all()

        class state:
            prev_results = set()

        def text_changed(entry):
            if entry.get_text_length() <= 2:
                for app in state.prev_results:
                    tray.remove_icon(app)
                state.prev_results.clear()
                return

            results = set()

            def on_result(app):
                results.add(app)
                if app in state.prev_results:
                    state.prev_results.remove(app)
                    return
                tray.add_icon("search-result", app, AppIcon(app, icon_config))

            def on_finish():
                for app in state.prev_results:
                    tray.remove_icon(app)
                state.prev_results = results

            search_index.search(
                entry.get_text().split(),
                on_result=on_result, on_finish=on_finish
            )
        self.__search_entry.connect("changed", text_changed)
