    def cmd_batch(
            self,
            tgt,
            fun,
            arg=(),
            tgt_type='glob',
            ret='',
            kwarg=None,
            batch='10%',
            **kwargs):
        '''
        Iteratively execute a command on subsets of minions at a time

        The function signature is the same as :py:meth:`cmd` with the
        following exceptions.

        :param batch: The batch identifier of systems to execute on

        :returns: A generator of minion returns

        .. code-block:: python

            >>> returns = local.cmd_batch('*', 'state.highstate', batch='10%')
            >>> for ret in returns:
            ...     print(ret)
            {'jerry': {...}}
            {'dave': {...}}
            {'stewart': {...}}
        '''
        if 'expr_form' in kwargs:
            salt.utils.versions.warn_until(
                'Fluorine',
                'The target type should be passed using the \'tgt_type\' '
                'argument instead of \'expr_form\'. Support for using '
                '\'expr_form\' will be removed in Salt Fluorine.'
            )
            tgt_type = kwargs.pop('expr_form')

        import salt.cli.batch
        arg = salt.utils.args.condition_input(arg, kwarg)
        opts = {'tgt': tgt,
                'fun': fun,
                'arg': arg,
                'tgt_type': tgt_type,
                'ret': ret,
                'batch': batch,
                'failhard': kwargs.get('failhard', False),
                'raw': kwargs.get('raw', False)}

        if 'timeout' in kwargs:
            opts['timeout'] = kwargs['timeout']
        if 'gather_job_timeout' in kwargs:
            opts['gather_job_timeout'] = kwargs['gather_job_timeout']
        if 'batch_wait' in kwargs:
            opts['batch_wait'] = int(kwargs['batch_wait'])

        eauth = {}
        if 'eauth' in kwargs:
            eauth['eauth'] = kwargs.pop('eauth')
        if 'username' in kwargs:
            eauth['username'] = kwargs.pop('username')
        if 'password' in kwargs:
            eauth['password'] = kwargs.pop('password')
        if 'token' in kwargs:
            eauth['token'] = kwargs.pop('token')

        for key, val in six.iteritems(self.opts):
            if key not in opts:
                opts[key] = val
        batch = salt.cli.batch.Batch(opts, eauth=eauth, quiet=True)
        for ret in batch.run():
            yield ret