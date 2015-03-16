
class AppHandler:
    
    def __iter__(self):
        raise NotImplementedError

    def handle_uri(self, uri):
        pass
