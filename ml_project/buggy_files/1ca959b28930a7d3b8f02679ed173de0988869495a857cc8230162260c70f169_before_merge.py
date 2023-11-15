    def remove_error_handler(self, callback):
        """Removes an error handler.

        Args:
            callback (:obj:`callable`): The error handler to remove.

        """
        if callback in self.error_handlers:
            self.error_handlers.remove(callback)