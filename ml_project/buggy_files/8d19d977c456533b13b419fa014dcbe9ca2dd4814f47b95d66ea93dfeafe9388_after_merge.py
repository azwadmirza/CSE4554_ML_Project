    def dispatch_error(self, update, error, promise=None):
        """Dispatches an error.

        Args:
            update (:obj:`str` | :class:`telegram.Update` | None): The update that caused the error
            error (:obj:`Exception`): The error that was raised.
            promise (:class:`telegram.utils.Promise`, optional): The promise whose pooled function
                raised the error.

        """
        async_args = None if not promise else promise.args
        async_kwargs = None if not promise else promise.kwargs

        if self.error_handlers:
            for callback, run_async in self.error_handlers.items():
                if self.use_context:
                    context = CallbackContext.from_error(update, error, self,
                                                         async_args=async_args,
                                                         async_kwargs=async_kwargs)
                    if run_async:
                        self.run_async(callback, update, context, update=update)
                    else:
                        callback(update, context)
                else:
                    if run_async:
                        self.run_async(callback, self.bot, update, error, update=update)
                    else:
                        callback(self.bot, update, error)

        else:
            self.logger.exception(
                'No error handlers are registered, logging exception.', exc_info=error)