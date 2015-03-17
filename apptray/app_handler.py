
class AppHandler:
    
    def __iter__(self):
        """
        Get all available applications.

        @return: list of L{apptray.app.App}
            The list of applications.
        """
        raise NotImplementedError

    def handle_uri(self, uri):
        """Handle a URI dragged to the main icon."""
