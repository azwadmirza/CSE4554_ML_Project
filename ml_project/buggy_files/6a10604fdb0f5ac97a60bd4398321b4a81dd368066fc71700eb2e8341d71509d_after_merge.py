    def handle_routine(self, que, opts, host, target):
        '''
        Run the routine in a "Thread", put a dict on the queue
        '''
        opts = copy.deepcopy(opts)
        single = Single(
                opts,
                opts['argv'],
                host,
                mods=self.mods,
                fsclient=self.fsclient,
                thin=self.thin,
                **target)
        ret = {'id': single.id}
        stdout, stderr, retcode = single.run()
        # This job is done, yield
        try:
            data = salt.utils.find_json(stdout)
            if len(data) < 2 and 'local' in data:
                ret['ret'] = data['local']
            else:
                ret['ret'] = {
                    'stdout': stdout,
                    'stderr': stderr,
                    'retcode': retcode,
                }
        except Exception:
            ret['ret'] = {
                'stdout': stdout,
                'stderr': stderr,
                'retcode': retcode,
            }
        que.put(ret)