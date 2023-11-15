    def job_not_running(self, jid, tgt, tgt_type, minions, is_finished):
        '''
        Return a future which will complete once jid (passed in) is no longer
        running on tgt
        '''
        ping_pub_data = yield self.saltclients['local'](tgt,
                                                        'saltutil.find_job',
                                                        [jid],
                                                        tgt_type=tgt_type)
        ping_tag = tagify([ping_pub_data['jid'], 'ret'], 'job')

        minion_running = False
        while True:
            try:
                event = self.application.event_listener.get_event(self,
                                                                  tag=ping_tag,
                                                                  timeout=self.application.opts['gather_job_timeout'])
                f = yield Any([event, is_finished])
                # When finished entire routine, cleanup other futures and return result
                if f is is_finished:
                    if not event.done():
                        event.set_result(None)
                    raise tornado.gen.Return(True)
                event = f.result()
            except TimeoutException:
                if not minion_running:
                    raise tornado.gen.Return(True)
                else:
                    ping_pub_data = yield self.saltclients['local'](tgt,
                                                                    'saltutil.find_job',
                                                                    [jid],
                                                                    tgt_type=tgt_type)
                    ping_tag = tagify([ping_pub_data['jid'], 'ret'], 'job')
                    minion_running = False
                    continue

            # Minions can return, we want to see if the job is running...
            if event['data'].get('return', {}) == {}:
                continue
            if event['data']['id'] not in minions:
                minions[event['data']['id']] = False
            minion_running = True