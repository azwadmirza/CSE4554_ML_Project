    def _disbatch_local(self, chunk):
        '''
        Dispatch local client commands
        '''
        # Generate jid before triggering a job to subscribe all returns from minions
        chunk['jid'] = salt.utils.jid.gen_jid(self.application.opts)

        # start listening for the event before we fire the job to avoid races
        events = [
            self.application.event_listener.get_event(self, tag='salt/job/'+chunk['jid']),
            self.application.event_listener.get_event(self, tag='syndic/job/'+chunk['jid']),
        ]

        f_call = self._format_call_run_job_async(chunk)
        # fire a job off
        pub_data = yield self.saltclients['local'](*f_call.get('args', ()), **f_call.get('kwargs', {}))

        # if the job didn't publish, lets not wait around for nothing
        # TODO: set header??
        if 'jid' not in pub_data:
            for future in events:
                try:
                    future.set_result(None)
                except Exception:
                    pass
            raise tornado.gen.Return('No minions matched the target. No command was sent, no jid was assigned.')

        # Map of minion_id -> returned for all minions we think we need to wait on
        minions = {m: False for m in pub_data['minions']}

        # minimum time required for return to complete. By default no waiting, if
        # we are a syndic then we must wait syndic_wait at a minimum
        min_wait_time = Future()
        min_wait_time.set_result(True)

        # wait syndic a while to avoid missing published events
        if self.application.opts['order_masters']:
            min_wait_time = tornado.gen.sleep(self.application.opts['syndic_wait'])

        # To ensure job_not_running and all_return are terminated by each other, communicate using a future
        is_finished = tornado.gen.sleep(self.application.opts['gather_job_timeout'])

        # ping until the job is not running, while doing so, if we see new minions returning
        # that they are running the job, add them to the list
        tornado.ioloop.IOLoop.current().spawn_callback(self.job_not_running, pub_data['jid'],
                                                      chunk['tgt'],
                                                      f_call['kwargs']['tgt_type'],
                                                      minions,
                                                      is_finished)

        def more_todo():
            '''Check if there are any more minions we are waiting on returns from
            '''
            return any(x is False for x in six.itervalues(minions))

        # here we want to follow the behavior of LocalClient.get_iter_returns
        # namely we want to wait at least syndic_wait (assuming we are a syndic)
        # and that there are no more jobs running on minions. We are allowed to exit
        # early if gather_job_timeout has been exceeded
        chunk_ret = {}
        while True:
            to_wait = events+[is_finished]
            if not min_wait_time.done():
                to_wait += [min_wait_time]

            def cancel_inflight_futures():
                for event in to_wait:
                    if not event.done():
                        event.set_result(None)
            f = yield Any(to_wait)
            try:
                # When finished entire routine, cleanup other futures and return result
                if f is is_finished:
                    cancel_inflight_futures()
                    raise tornado.gen.Return(chunk_ret)
                elif f is min_wait_time:
                    if not more_todo():
                        cancel_inflight_futures()
                        raise tornado.gen.Return(chunk_ret)
                    continue
                f_result = f.result()
                # if this is a start, then we need to add it to the pile
                if f_result['tag'].endswith('/new'):
                    for minion_id in f_result['data']['minions']:
                        if minion_id not in minions:
                            minions[minion_id] = False
                else:
                    chunk_ret[f_result['data']['id']] = f_result['data']['return']
                    # clear finished event future
                    minions[f_result['data']['id']] = True

                    # if there are no more minions to wait for, then we are done
                    if not more_todo() and min_wait_time.done():
                        cancel_inflight_futures()
                        raise tornado.gen.Return(chunk_ret)

            except TimeoutException:
                pass

            if f == events[0]:
                events[0] = self.application.event_listener.get_event(self, tag='salt/job/'+chunk['jid'])
            else:
                events[1] = self.application.event_listener.get_event(self, tag='syndic/job/'+chunk['jid'])