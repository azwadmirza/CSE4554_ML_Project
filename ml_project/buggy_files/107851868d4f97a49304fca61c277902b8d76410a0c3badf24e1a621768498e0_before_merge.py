    def get_cli_event_returns(
            self,
            jid,
            minions,
            timeout=None,
            tgt='*',
            tgt_type='glob',
            verbose=False,
            progress=False,
            show_timeout=False,
            show_jid=False,
            **kwargs):
        '''
        Get the returns for the command line interface via the event system
        '''
        log.trace('func get_cli_event_returns()')

        if 'expr_form' in kwargs:
            salt.utils.warn_until(
                'Fluorine',
                'The target type should be passed using the \'tgt_type\' '
                'argument instead of \'expr_form\'. Support for using '
                '\'expr_form\' will be removed in Salt Fluorine.'
            )
            tgt_type = kwargs.pop('expr_form')

        if verbose:
            msg = 'Executing job with jid {0}'.format(jid)
            print(msg)
            print('-' * len(msg) + '\n')
        elif show_jid:
            print('jid: {0}'.format(jid))

        # lazy load the connected minions
        connected_minions = None
        return_count = 0

        for ret in self.get_iter_returns(jid,
                                         minions,
                                         timeout=timeout,
                                         tgt=tgt,
                                         tgt_type=tgt_type,
                                         expect_minions=(verbose or show_timeout),
                                         **kwargs
                                         ):
            log.debug('return event: %s', ret)
            return_count = return_count + 1
            if progress:
                for id_, min_ret in six.iteritems(ret):
                    if not min_ret.get('failed') is True:
                        yield {'minion_count': len(minions), 'return_count': return_count}
            # replace the return structure for missing minions
            for id_, min_ret in six.iteritems(ret):
                if min_ret.get('failed') is True:
                    if connected_minions is None:
                        connected_minions = salt.utils.minions.CkMinions(self.opts).connected_ids()
                    if self.opts['minion_data_cache'] \
                            and salt.cache.factory(self.opts).contains('minions/{0}'.format(id_), 'data') \
                            and connected_minions \
                            and id_ not in connected_minions:

                        yield {id_: {'out': 'no_return',
                                     'ret': 'Minion did not return. [Not connected]'}}
                    else:
                        # don't report syndics as unresponsive minions
                        if not os.path.exists(os.path.join(self.opts['syndic_dir'], id_)):
                            yield {id_: {'out': 'no_return',
                                         'ret': 'Minion did not return. [No response]'}}
                else:
                    yield {id_: min_ret}

        self._clean_up_subscriptions(jid)