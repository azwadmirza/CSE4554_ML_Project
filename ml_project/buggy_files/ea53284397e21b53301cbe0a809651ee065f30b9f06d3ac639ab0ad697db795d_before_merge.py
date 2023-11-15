    def add_error_handler(self, callback):
        """Registers an error handler in the Dispatcher. This handler will receive every error
        which happens in your bot.

        Warning: The errors handled within these handlers won't show up in the logger, so you
        need to make sure that you reraise the error.

        Args:
            callback (:obj:`callable`): The callback function for this error handler. Will be
                called when an error is raised. Callback signature for context based API:

                ``def callback(update: Update, context: CallbackContext)``

                The error that happened will be present in context.error.

        Note:
            See https://git.io/fxJuV for more info about switching to context based API.
        """
        self.error_handlers.append(callback)