    def dispatchTo(self, handlers, update, **kwargs):
        """
        Dispatches an update to a list of handlers.

        Args:
            handlers (list): A list of handler-functions.
            update (any): The update to be dispatched
        """

        for handler in handlers:
            self.call_handler(handler, update, **kwargs)