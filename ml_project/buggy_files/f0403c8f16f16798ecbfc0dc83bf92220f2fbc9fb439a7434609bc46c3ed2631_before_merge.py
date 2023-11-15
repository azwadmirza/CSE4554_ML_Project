    def get_cli_static_event_returns(
            self,
            jid,
            minions,
            timeout=None,
            tgt='*',
            tgt_type='glob',
            verbose=False,
            show_timeout=False,
            show_jid=False):
        '''
        Get the returns for the command line interface via the event system
        '''
        log.trace('entered - function get_cli_static_event_returns()')
        minions = set(minions)
        if verbose:
            msg = 'Executing job with jid {0}'.format(jid)
            print(msg)
            print('-' * len(msg) + '\n')
        elif show_jid:
            print('jid: {0}'.format(jid))

        if timeout is None:
            timeout = self.opts['timeout']

        start = int(time.time())
        timeout_at = start + timeout
        found = set()
        ret = {}
        # Check to see if the jid is real, if not return the empty dict
        try:
            if self.returners['{0}.get_load'.format(self.opts['master_job_cache'])](jid) == {}:
                log.warning('jid does not exist')
                return ret
        except Exception as exc:
            raise SaltClientError('Load could not be retrieved from '
                                  'returner {0}. Exception details: {1}'.format(
                                      self.opts['master_job_cache'],
                                      exc))
        # Wait for the hosts to check in
        while True:
            # Process events until timeout is reached or all minions have returned
            time_left = timeout_at - int(time.time())
            # Wait 0 == forever, use a minimum of 1s
            wait = max(1, time_left)
            jid_tag = 'salt/job/{0}'.format(jid)
            raw = self.event.get_event(wait, jid_tag)
            if raw is not None and 'return' in raw:
                if 'minions' in raw.get('data', {}):
                    minions.update(raw['data']['minions'])
                    continue
                found.add(raw['id'])
                ret[raw['id']] = {'ret': raw['return']}
                ret[raw['id']]['success'] = raw.get('success', False)
                if 'out' in raw:
                    ret[raw['id']]['out'] = raw['out']
                if len(found.intersection(minions)) >= len(minions):
                    # All minions have returned, break out of the loop
                    break
                continue
            # Then event system timeout was reached and nothing was returned
            if len(found.intersection(minions)) >= len(minions):
                # All minions have returned, break out of the loop
                break
            if int(time.time()) > timeout_at:
                if verbose or show_timeout:
                    if self.opts.get('minion_data_cache', False) \
                            or tgt_type in ('glob', 'pcre', 'list'):
                        if len(found) < len(minions):
                            fail = sorted(list(minions.difference(found)))
                            for minion in fail:
                                ret[minion] = {
                                    'out': 'no_return',
                                    'ret': 'Minion did not return'
                                }
                break
            time.sleep(0.01)

        self._clean_up_subscriptions(jid)
        return ret