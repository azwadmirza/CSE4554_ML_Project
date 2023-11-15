    def run_job(
            self,
            tgt,
            fun,
            arg=(),
            expr_form='glob',
            ret='',
            timeout=None,
            jid='',
            kwarg=None,
            **kwargs):
        '''
        Asynchronously send a command to connected minions

        Prep the job directory and publish a command to any targeted minions.

        :return: A dictionary of (validated) ``pub_data`` or an empty
            dictionary on failure. The ``pub_data`` contains the job ID and a
            list of all minions that are expected to return data.

        .. code-block:: python

            >>> local.run_job('*', 'test.sleep', [300])
            {'jid': '20131219215650131543', 'minions': ['jerry']}
        '''
        arg = salt.utils.args.condition_input(arg, kwarg)

        # Subscribe to all events and subscribe as early as possible
        self.event.subscribe(jid)

        pub_data = self.pub(
            tgt,
            fun,
            arg,
            expr_form,
            ret,
            jid=jid,
            timeout=self._get_timeout(timeout),
            **kwargs)

        return self._check_pub_data(pub_data)