    def handle_update(self, update, dispatcher, check_result, context=None):
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance. Calls :attr:`callback` along with its respectful
        arguments. To work with the :class:`telegram.ext.ConversationHandler`, this method
        returns the value returned from :attr:`callback`.
        Note that it can be overridden if needed by the subclassing handler.

        Args:
            update (:obj:`str` | :class:`telegram.Update`): The update to be handled.
            dispatcher (:class:`telegram.ext.Dispatcher`): The calling dispatcher.
            check_result: The result from :attr:`check_update`.

        """
        if context:
            self.collect_additional_context(context, update, dispatcher, check_result)
            if self.run_async:
                return dispatcher.run_async(self.callback, update, context, update=update)
            else:
                return self.callback(update, context)
        else:
            optional_args = self.collect_optional_args(dispatcher, update, check_result)
            if self.run_async:
                return dispatcher.run_async(self.callback, dispatcher.bot, update, update=update,
                                            **optional_args)
            else:
                return self.callback(dispatcher.bot, update, **optional_args)