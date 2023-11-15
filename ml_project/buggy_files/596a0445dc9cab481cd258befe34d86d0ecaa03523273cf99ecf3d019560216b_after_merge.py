    def cmd_subset(
            self,
            tgt,
            fun,
            arg=(),
            tgt_type='glob',
            ret='',
            kwarg=None,
            sub=3,
            cli=False,
            progress=False,
            **kwargs):
        '''
        Execute a command on a random subset of the targeted systems

        The function signature is the same as :py:meth:`cmd` with the
        following exceptions.

        :param sub: The number of systems to execute on
        :param cli: When this is set to True, a generator is returned,
                    otherwise a dictionary of the minion returns is returned

        .. code-block:: python

            >>> SLC.cmd_subset('*', 'test.ping', sub=1)
            {'jerry': True}
        '''
        if 'expr_form' in kwargs:
            salt.utils.warn_until(
                'Fluorine',
                'The target type should be passed using the \'tgt_type\' '
                'argument instead of \'expr_form\'. Support for using '
                '\'expr_form\' will be removed in Salt Fluorine.'
            )
            tgt_type = kwargs.pop('expr_form')

        minion_ret = self.cmd(tgt,
                              'sys.list_functions',
                              tgt_type=tgt_type,
                              **kwargs)
        minions = list(minion_ret)
        random.shuffle(minions)
        f_tgt = []
        for minion in minions:
            if fun in minion_ret[minion]:
                f_tgt.append(minion)
            if len(f_tgt) >= sub:
                break
        func = self.cmd
        if cli:
            func = self.cmd_cli
        return func(
                f_tgt,
                fun,
                arg,
                tgt_type='list',
                ret=ret,
                kwarg=kwarg,
                progress=progress,
                **kwargs)