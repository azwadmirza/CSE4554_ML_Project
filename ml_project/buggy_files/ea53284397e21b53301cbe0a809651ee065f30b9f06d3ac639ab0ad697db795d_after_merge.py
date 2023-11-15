    def add_error_handler(self, callback, run_async=False):
        """Registers an error handler in the Dispatcher. This handler will receive every error
        which happens in your bot.

        Note:
            Attempts to add the same callback multiple times will be ignored.

        Warning:
            The errors handled within these handlers won't show up in the logger, so you
            need to make sure that you reraise the error.

        Args:
            callback (:obj:`callable`): The callback function for this error handler. Will be
                called when an error is raised. Callback signature for context based API:

                ``def callback(update: Update, context: CallbackContext)``

                The error that happened will be present in context.error.
            run_async (:obj:`bool`, optional): Whether this handlers callback should be run
                asynchronously using :meth:`run_async`. Defaults to :obj:`False`.

        Note:
            See https://git.io/fxJuV for more info about switching to context based API.
        """
        if callback in self.error_handlers:
            self.logger.debug('The callback is already registered as an error handler. Ignoring.')
            return
        self.error_handlers[callback] = run_async