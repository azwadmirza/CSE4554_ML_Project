    def get_returns(
            self,
            jid,
            minions,
            timeout=None):
        '''
        Get the returns for the command line interface via the event system
        '''
        minions = set(minions)
        if timeout is None:
            timeout = self.opts['timeout']
        start = int(time.time())
        timeout_at = start + timeout
        log.debug(
            'get_returns for jid {0} sent to {1} will timeout at {2}'.format(
                jid, minions, datetime.fromtimestamp(timeout_at).time()
            )
        )

        found = set()
        ret = {}
        # Check to see if the jid is real, if not return the empty dict
        try:
            if self.returners['{0}.get_load'.format(self.opts['master_job_cache'])](jid) == {}:
                log.warning('jid does not exist')
                return ret
        except Exception as exc:
            raise SaltClientError('Master job cache returner [{0}] failed to verify jid. '
                                  'Exception details: {1}'.format(self.opts['master_job_cache'], exc))

        # Wait for the hosts to check in
        while True:
            time_left = timeout_at - int(time.time())
            wait = max(1, time_left)
            raw = self.event.get_event(wait, jid, auto_reconnect=self.auto_reconnect)
            if raw is not None and 'return' in raw:
                found.add(raw['id'])
                ret[raw['id']] = raw['return']
                if len(found.intersection(minions)) >= len(minions):
                    # All minions have returned, break out of the loop
                    log.debug('jid {0} found all minions'.format(jid))
                    break
                continue
            # Then event system timeout was reached and nothing was returned
            if len(found.intersection(minions)) >= len(minions):
                # All minions have returned, break out of the loop
                log.debug('jid {0} found all minions'.format(jid))
                break
            if int(time.time()) > timeout_at:
                log.info(
                    'jid {0} minions {1} did not return in time'.format(
                        jid, (minions - found)
                    )
                )
                break
            time.sleep(0.01)
        return ret