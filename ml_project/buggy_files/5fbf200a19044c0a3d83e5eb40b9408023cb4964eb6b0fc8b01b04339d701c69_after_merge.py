    def cmd_iter_no_block(
            self,
            tgt,
            fun,
            arg=(),
            timeout=None,
            expr_form='glob',
            ret='',
            kwarg=None,
            show_jid=False,
            **kwargs):
        '''
        Yields the individual minion returns as they come in, or None
            when no returns are available.

        The function signature is the same as :py:meth:`cmd` with the
        following exceptions.

        :returns: A generator yielding the individual minion returns, or None
            when no returns are available. This allows for actions to be
            injected in between minion returns.

        .. code-block:: python

            >>> ret = local.cmd_iter_no_block('*', 'test.ping')
            >>> for i in ret:
            ...     print(i)
            None
            {'jerry': {'ret': True}}
            {'dave': {'ret': True}}
            None
            {'stewart': {'ret': True}}
        '''
        arg = salt.utils.args.condition_input(arg, kwarg)
        pub_data = self.run_job(
            tgt,
            fun,
            arg,
            expr_form,
            ret,
            timeout,
            **kwargs)

        if not pub_data:
            yield pub_data
        else:
            for fn_ret in self.get_iter_returns(pub_data['jid'],
                                                pub_data['minions'],
                                                timeout=timeout,
                                                tgt=tgt,
                                                tgt_type=expr_form,
                                                block=False,
                                                **kwargs):
                if fn_ret and show_jid:
                    for minion in fn_ret.keys():
                        fn_ret[minion]['jid'] = pub_data['jid']
                yield fn_ret

            self._clean_up_subscriptions(pub_data['jid'])