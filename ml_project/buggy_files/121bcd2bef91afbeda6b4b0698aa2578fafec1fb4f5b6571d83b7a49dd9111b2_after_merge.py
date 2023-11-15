    def cmd(
            self,
            tgt,
            fun,
            arg=(),
            timeout=None,
            expr_form='glob',
            ret='',
            kwarg=None,
            **kwargs):
        '''
        The cmd method will execute and wait for the timeout period for all
        minions to reply, then it will return all minion data at once.

        Usage:

        .. code-block:: python

            import salt.client
            client = salt.client.LocalClient()
            ret = client.cmd('*', 'cmd.run', ['whoami'])

        With authentication:

        .. code-block:: yaml

            # Master config
            ...
            external_auth:
              pam:
                fred:
                  - test.*
            ...


        .. code-block:: python

            ret = client.cmd('*', 'test.ping', [], username='fred', password='pw', eauth='pam')

        With extra keyword arguments for the command function to be run:

        .. code-block:: python

            ret = client.cmd('*', 'test.arg', ['arg1', 'arg2'], kwarg={ 'foo': 'bar'})

        Compound command usage:

        .. code-block:: python

            ret = client.cmd('*', ['grains.items', 'cmd.run'], [[], ['whoami']])

        :param tgt: Which minions to target for the execution. Default is shell
            glob. Modified by the ``expr_form`` option.
        :type tgt: string or list

        :param fun: The module and function to call on the specified minions of
            the form ``module.function``. For example ``test.ping`` or
            ``grains.items``.

            Compound commands
                Multiple functions may be called in a single publish by
                passing a list of commands. This can dramatically lower
                overhead and speed up the application communicating with Salt.

                This requires that the ``arg`` param is a list of lists. The
                ``fun`` list and the ``arg`` list must correlate by index
                meaning a function that does not take arguments must still have
                a corresponding empty list at the expected index.
        :type fun: string or list of strings

        :param arg: A list of arguments to pass to the remote function. If the
            function takes no arguments ``arg`` may be omitted except when
            executing a compound command.
        :type arg: list or list-of-lists

        :param timeout: Seconds to wait after the last minion returns but
            before all minions return.

        :param expr_form: The type of ``tgt``. Allowed values:

            * ``glob`` - Bash glob completion - Default
            * ``pcre`` - Perl style regular expression
            * ``list`` - Python list of hosts
            * ``grain`` - Match based on a grain comparison
            * ``grain_pcre`` - Grain comparison with a regex
            * ``pillar`` - Pillar data comparison
            * ``nodegroup`` - Match on nodegroup
            * ``range`` - Use a Range server for matching
            * ``compound`` - Pass a compound match string

        :param ret: The returner to use. The value passed can be single
            returner, or a comma delimited list of returners to call in order
            on the minions

        :param kwarg: A dictionary with keyword arguments for the function.

        :param kwargs: Optional keyword arguments.

            Authentication credentials may be passed when using
            :conf_master:`external_auth`.

            * ``eauth`` - the external_auth backend
            * ``username`` and ``password``
            * ``token``

        :returns: A dictionary with the result of the execution, keyed by
            minion ID. A compound command will return a sub-dictionary keyed by
            function name.
        '''
        arg = condition_kwarg(arg, kwarg)
        pub_data = self.run_job(tgt,
                                fun,
                                arg,
                                expr_form,
                                ret,
                                timeout,
                                **kwargs)

        if not pub_data:
            return pub_data

        return self.get_returns(pub_data['jid'],
                                pub_data['minions'],
                                self._get_timeout(timeout))