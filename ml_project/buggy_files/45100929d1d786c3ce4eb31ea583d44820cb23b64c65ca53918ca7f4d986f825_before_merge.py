    def get_event_iter_returns(self, jid, minions, timeout=None):
        '''
        Gather the return data from the event system, break hard when timeout
        is reached.
        '''
        log.trace('entered - function get_event_iter_returns()')
        if timeout is None:
            timeout = self.opts['timeout']

        timeout_at = time.time() + timeout

        found = set()
        # Check to see if the jid is real, if not return the empty dict
        if self.returners['{0}.get_load'.format(self.opts['master_job_cache'])](jid) == {}:
            log.warning('jid does not exist')
            yield {}
            # stop the iteration, since the jid is invalid
            raise StopIteration()
        # Wait for the hosts to check in
        while True:
            raw = self.event.get_event(timeout)
            if raw is None or time.time() > timeout_at:
                # Timeout reached
                break
            if 'minions' in raw.get('data', {}):
                continue
            found.add(raw['id'])
            ret = {raw['id']: {'ret': raw['return']}}
            if 'out' in raw:
                ret[raw['id']]['out'] = raw['out']
            yield ret
            time.sleep(0.02)