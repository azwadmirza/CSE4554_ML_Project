    def call_handler(self, handler, update):
        """
        Calls an update handler. Checks the handler for keyword arguments and
        fills them, if possible.

        Args:
            handler (function): An update handler function
            update (any): An update
        """
        kwargs = {}
        fargs = getargspec(handler).args

        if 'update_queue' in fargs:
            kwargs['update_queue'] = self.update_queue

        if 'args' in fargs:
            if isinstance(update, Update):
                args = update.message.text.split(' ')[1:]
            elif isinstance(update, str):
                args = update.split(' ')[1:]
            else:
                args = None

            kwargs['args'] = args

        handler(self.bot, update, **kwargs)