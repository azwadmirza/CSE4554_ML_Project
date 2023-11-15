    def run(self):
        '''
        Execute the overall routine
        '''
        fstr = '{0}.prep_jid'.format(self.opts['master_job_cache'])
        jid = self.returners[fstr]()

        # Save the invocation information
        argv = self.opts['argv']

        if self.opts['raw_shell']:
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
        self.returners['{0}.save_load'.format(self.opts['master_job_cache'])](jid, job_load)

        if self.opts.get('verbose'):
            msg = 'Executing job with jid {0}'.format(jid)
            print(msg)
            print('-' * len(msg) + '\n')
            print('')
        sret = {}
        outputter = self.opts.get('output', 'nested')
        for ret in self.handle_ssh():
            host = ret.keys()[0]
            self.cache_job(jid, host, ret[host])
            ret = self.key_deploy(host, ret)
            if not isinstance(ret[host], dict):
                p_data = {host: ret[host]}
            if 'return' not in ret[host]:
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
                self.event.fire_event(
                        ret,
                        salt.utils.event.tagify(
                            [jid, 'ret', host],
                            'job'))
        if self.opts.get('static'):
            salt.output.display_output(
                    sret,
                    outputter,
                    self.opts)