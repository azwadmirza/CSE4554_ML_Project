    def get_iter_returns(
            self,
            jid,
            minions,
            timeout=None,
            tgt='*',
            tgt_type='glob',
            expect_minions=False,
            **kwargs):
        '''
        Watch the event system and return job data as it comes in

        :returns: all of the information for the JID
        '''
        if not isinstance(minions, set):
            if isinstance(minions, string_types):
                minions = set([minions])
            elif isinstance(minions, (list, tuple)):
                minions = set(list(minions))

        if timeout is None:
            timeout = self.opts['timeout']
        start = int(time.time())
        timeout_at = start + timeout

        # timeouts per minion, id_ -> timeout time
        minion_timeouts = {}

        found = set()
        # Check to see if the jid is real, if not return the empty dict
        if not self.returners['{0}.get_load'.format(self.opts['master_job_cache'])](jid) != {}:
            log.warning('jid does not exist')
            yield {}
            # stop the iteration, since the jid is invalid
            raise StopIteration()
        # Wait for the hosts to check in
        syndic_wait = 0
        last_time = False
        log.debug(
            'get_iter_returns for jid {0} sent to {1} will timeout at {2}'.format(
                jid, minions, datetime.fromtimestamp(timeout_at).time()
            )
        )
        # iterator for this job's return
        ret_iter = self.get_returns_no_block(jid)
        # iterator for the info of this job
        jinfo_iter = []
        jinfo_timeout = time.time() + timeout
        while True:
            # Process events until timeout is reached or all minions have returned
            for raw in ret_iter:
                # if we got None, then there were no events
                if raw is None:
                    break

                if 'minions' in raw.get('data', {}):
                    minions.update(raw['data']['minions'])
                    continue
                if 'syndic' in raw:
                    minions.update(raw['syndic'])
                    continue
                if 'return' not in raw['data']:
                    continue
                if kwargs.get('raw', False):
                    found.add(raw['data']['id'])
                    yield raw
                else:
                    found.add(raw['data']['id'])
                    ret = {raw['data']['id']: {'ret': raw['data']['return']}}
                    if 'out' in raw:
                        ret[raw['data']['id']]['out'] = raw['data']['out']
                    log.debug('jid {0} return from {1}'.format(jid, raw['data']['id']))
                    yield ret

            # if we have all of the returns, no need for anything fancy
            if len(found.intersection(minions)) >= len(minions):
                # All minions have returned, break out of the loop
                log.debug('jid {0} found all minions {1}'.format(jid, found))
                if self.opts['order_masters']:
                    if syndic_wait < self.opts.get('syndic_wait', 1):
                        syndic_wait += 1
                        timeout_at = int(time.time()) + 1
                        log.debug('jid {0} syndic_wait {1} will now timeout at {2}'.format(
                                  jid, syndic_wait, datetime.fromtimestamp(timeout_at).time()))
                        continue
                break

            # let start the timeouts for all remaining minions
            missing_minions = minions - found
            for id_ in missing_minions:
                # if we have a new minion in the list, make sure it has a timeout
                if id_ not in minion_timeouts:
                    minion_timeouts[id_] = time.time() + timeout

            # if we don't have the job info iterator (or its timed out),
            # lets make it assuming we have more minions to ping for
            if time.time() > jinfo_timeout and missing_minions:
                # need our own event listener, so we don't clobber the class one
                event = salt.utils.event.get_event(
                        'master',
                        self.opts['sock_dir'],
                        self.opts['transport'],
                        opts=self.opts,
                        listen=not self.opts.get('__worker', False))
                # start listening for new events, before firing off the pings
                event.connect_pub()
                jinfo = self.gather_job_info(jid, tgt, tgt_type)
                # if we weren't assigned any jid that means the master thinks
                # we have nothing to send
                if 'jid' not in jinfo:
                    jinfo_iter = []
                else:
                    jinfo_iter = self.get_returns_no_block(jinfo['jid'], event=event)
                jinfo_timeout = time.time() + self.opts['gather_job_timeout']

            # check for minions that are running the job still
            for raw in jinfo_iter:
                # if there are no more events, lets stop waiting for the jinfo
                if raw is None:
                    break

                # TODO: move to a library??
                if 'minions' in raw.get('data', {}):
                    minions.update(raw['data']['minions'])
                    continue
                if 'syndic' in raw.get('data', {}):
                    minions.update(raw['syndic'])
                    continue
                if 'return' not in raw.get('data', {}):
                    continue

                # if the job isn't running there anymore... don't count
                if raw['data']['return'] == {}:
                    continue

                # if we didn't originally target the minion, lets add it to the list
                if raw['data']['id'] not in minions:
                    minions.add(raw['data']['id'])
                # update this minion's timeout, as long as the job is still running
                minion_timeouts[raw['data']['id']] = time.time() + timeout

            # if we have hit gather_job_timeout (after firing the job) AND
            # if we have hit all minion timeouts, lets call it
            now = time.time()
            # if we have finished pinging all the minions
            done = now > jinfo_timeout
            # only check minion timeouts if the ping job is all done
            if done:
                # if all minions have timeod out
                for id_ in minions - found:
                    if now < minion_timeouts[id_]:
                        done = False
                        break
            if done:
                break

            # don't spin
            time.sleep(0.01)
        if expect_minions:
            for minion in list((minions - found)):
                yield {minion: {'failed': True}}