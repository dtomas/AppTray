from apptray.sendto_item import SendToItem, SendToItemNotCreated


class SendToHandler:
    
    def __init__(self):
        self.__sendto_items = {}

    def app_added(self, app):
        for mime_type in app.mime_types:
            if not mime_type or not mime_type.strip(' '):
                continue
            try:
                self.__sendto_items.setdefault(app, []).append(SendToItem(app, mime_type))
            except SendToItemNotCreated:
                pass

    def app_removed(self, app):
        for sendto_item in self.__sendto_items.get(app, []):
            sendto_item.remove()
