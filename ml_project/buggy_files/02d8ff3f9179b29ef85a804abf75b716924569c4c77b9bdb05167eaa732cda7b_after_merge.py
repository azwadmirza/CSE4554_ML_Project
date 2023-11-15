    def call_handler(self, handler, update, **kwargs):
        """
        Calls an update handler. Checks the handler for keyword arguments and
        fills them, if possible.

        Args:
            handler (function): An update handler function
            update (any): An update
        """

        target_kwargs = {}
        fargs = getargspec(handler).args

        '''
        async handlers will receive all optional arguments, since we can't
        their argument list.
        '''

        is_async = 'pargs' == getargspec(handler).varargs

        if is_async or 'update_queue' in fargs:
            target_kwargs['update_queue'] = self.update_queue

        if is_async or 'args' in fargs:
            if isinstance(update, Update):
                args = update.message.text.split(' ')[1:]
            elif isinstance(update, str):
                args = update.split(' ')[1:]
            else:
                args = None

            target_kwargs['args'] = args

        if is_async or 'groups' in fargs:
            target_kwargs['groups'] = kwargs.get('groups', None)

        if is_async or 'groupdict' in fargs:
            target_kwargs['groupdict'] = kwargs.get('groupdict', None)

        handler(self.bot, update, **target_kwargs)