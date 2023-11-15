    def cmd_async(
            self,
            tgt,
            fun,
            arg=(),
            tgt_type='glob',
            ret='',
            jid='',
            kwarg=None,
            **kwargs):
        '''
        Asynchronously send a command to connected minions

        The function signature is the same as :py:meth:`cmd` with the
        following exceptions.

        :returns: A job ID or 0 on failure.

        .. code-block:: python

            >>> local.cmd_async('*', 'test.sleep', [300])
            '20131219215921857715'
        '''
        arg = salt.utils.args.condition_input(arg, kwarg)
        pub_data = self.run_job(tgt,
                                fun,
                                arg,
                                tgt_type,
                                ret,
                                jid=jid,
                                listen=False,
                                **kwargs)
        try:
            return pub_data['jid']
        except KeyError:
            return 0