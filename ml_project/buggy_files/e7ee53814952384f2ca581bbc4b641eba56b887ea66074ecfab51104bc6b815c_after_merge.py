    def handle_ssh(self, mine=False):
        '''
        Spin up the needed threads or processes and execute the subsequent
        routines
        '''
        que = multiprocessing.Queue()
        running = {}
        target_iter = self.targets.__iter__()
        returned = set()
        rets = set()
        init = False
        while True:
            if not self.targets:
                log.error('No matching targets found in roster.')
                break
            if len(running) < self.opts.get('ssh_max_procs', 25) and not init:
                try:
                    host = next(target_iter)
                except StopIteration:
                    init = True
                    continue
                for default in self.defaults:
                    if default not in self.targets[host]:
                        self.targets[host][default] = self.defaults[default]
                if 'host' not in self.targets[host]:
                    self.targets[host]['host'] = host
                args = (
                        que,
                        self.opts,
                        host,
                        self.targets[host],
                        mine,
                        )
                routine = MultiprocessingProcess(
                                target=self.handle_routine,
                                args=args)
                routine.start()
                running[host] = {'thread': routine}
                continue
            ret = {}
            try:
                ret = que.get(False)
                if 'id' in ret:
                    returned.add(ret['id'])
                    yield {ret['id']: ret['ret']}
            except Exception:
                # This bare exception is here to catch spurious exceptions
                # thrown by que.get during healthy operation. Please do not
                # worry about this bare exception, it is entirely here to
                # control program flow.
                pass
            for host in running:
                if not running[host]['thread'].is_alive():
                    if host not in returned:
                        # Try to get any returns that came through since we
                        # last checked
                        try:
                            while True:
                                ret = que.get(False)
                                if 'id' in ret:
                                    returned.add(ret['id'])
                                    yield {ret['id']: ret['ret']}
                        except Exception:
                            pass

                        if host not in returned:
                            error = ('Target \'{0}\' did not return any data, '
                                     'probably due to an error.').format(host)
                            ret = {'id': host,
                                   'ret': error}
                            log.error(error)
                            yield {ret['id']: ret['ret']}
                    running[host]['thread'].join()
                    rets.add(host)
            for host in rets:
                if host in running:
                    running.pop(host)
            if len(rets) >= len(self.targets):
                break
            # Sleep when limit or all threads started
            if len(running) >= self.opts.get('ssh_max_procs', 25) or len(self.targets) >= len(running):
                time.sleep(0.1)