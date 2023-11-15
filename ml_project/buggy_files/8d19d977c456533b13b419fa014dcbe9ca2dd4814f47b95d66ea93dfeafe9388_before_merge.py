    def dispatch_error(self, update, error):
        """Dispatches an error.

        Args:
            update (:obj:`str` | :class:`telegram.Update` | None): The update that caused the error
            error (:obj:`Exception`): The error that was raised.

        """
        if self.error_handlers:
            for callback in self.error_handlers:
                if self.use_context:
                    callback(update, CallbackContext.from_error(update, error, self))
                else:
                    callback(self.bot, update, error)

        else:
            self.logger.exception(
                'No error handlers are registered, logging exception.', exc_info=error)