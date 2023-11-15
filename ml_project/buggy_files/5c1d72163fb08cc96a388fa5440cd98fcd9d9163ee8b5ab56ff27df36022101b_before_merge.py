    def run(self, jid=None):
        '''
        Execute the overall routine, print results via outputters
        '''
        if self.opts['list_hosts']:
            self._get_roster()
            ret = {}
            for roster_file in self.__parsed_rosters:
                if roster_file.startswith('#'):
                    continue
                ret[roster_file] = {}
                for host_id in self.__parsed_rosters[roster_file]:
                    hostname = self.__parsed_rosters[roster_file][host_id]['host']
                    ret[roster_file][host_id] = hostname
            salt.output.display_output(ret, 'nested', self.opts)
            sys.exit()

        fstr = '{0}.prep_jid'.format(self.opts['master_job_cache'])
        jid = self.returners[fstr](passed_jid=jid or self.opts.get('jid', None))

        # Save the invocation information
        argv = self.opts['argv']

        if self.opts.get('raw_shell', False):
            fun = 'ssh._raw'
            args = argv
        else:
            fun = argv[0] if argv else ''
            args = argv[1:]

        job_load = {
            'jid': jid,
            'tgt_type': self.tgt_type,
            'tgt': self.opts['tgt'],
            'user': self.opts['user'],
            'fun': fun,
            'arg': args,
            }

        # save load to the master job cache
        try:
            if isinstance(jid, bytes):
                jid = jid.decode('utf-8')
            if self.opts['master_job_cache'] == 'local_cache':
                self.returners['{0}.save_load'.format(self.opts['master_job_cache'])](jid, job_load, minions=self.targets.keys())
            else:
                self.returners['{0}.save_load'.format(self.opts['master_job_cache'])](jid, job_load)
        except Exception as exc:
            log.exception(exc)
            log.error(
                'Could not save load with returner %s: %s',
                self.opts['master_job_cache'], exc
            )

        if self.opts.get('verbose'):
            msg = 'Executing job with jid {0}'.format(jid)
            print(msg)
            print('-' * len(msg) + '\n')
            print('')
        sret = {}
        outputter = self.opts.get('output', 'nested')
        final_exit = 0
        for ret in self.handle_ssh():
            host = next(six.iterkeys(ret))
            if isinstance(ret[host], dict):
                host_ret = ret[host].get('retcode', 0)
                if host_ret != 0:
                    final_exit = 1
            else:
                # Error on host
                final_exit = 1

            self.cache_job(jid, host, ret[host], fun)
            ret = self.key_deploy(host, ret)

            if isinstance(ret[host], dict) and (ret[host].get('stderr') or '').startswith('ssh:'):
                ret[host] = ret[host]['stderr']

            if not isinstance(ret[host], dict):
                p_data = {host: ret[host]}
            elif 'return' not in ret[host]:
                p_data = ret
            else:
                outputter = ret[host].get('out', self.opts.get('output', 'nested'))
                p_data = {host: ret[host].get('return', {})}
            if self.opts.get('static'):
                sret.update(p_data)
            else:
                salt.output.display_output(
                        p_data,
                        outputter,
                        self.opts)
            if self.event:
                id_, data = next(six.iteritems(ret))
                if isinstance(data, six.text_type):
                    data = {'return': data}
                if 'id' not in data:
                    data['id'] = id_
                data['jid'] = jid  # make the jid in the payload the same as the jid in the tag
                self.event.fire_event(
                    data,
                    salt.utils.event.tagify(
                        [jid, 'ret', host],
                        'job'))
        if self.opts.get('static'):
            salt.output.display_output(
                    sret,
                    outputter,
                    self.opts)
        if final_exit:
            sys.exit(salt.defaults.exitcodes.EX_AGGREGATE)