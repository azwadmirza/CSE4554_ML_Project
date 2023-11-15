    def __getitem__(self, cmd):
        '''
        Return the function call to simulate the salt local lookup system
        '''
        if '.' not in cmd and not self.cmd_prefix:
            # Form of salt.cmd.run in Jinja -- it's expecting a subdictionary
            # containing only 'cmd' module calls, in that case. Create a new
            # FunctionWrapper which contains the prefix 'cmd' (again, for the
            # salt.cmd.run example)
            kwargs = copy.deepcopy(self.kwargs)
            id_ = kwargs.pop('id_')
            host = kwargs.pop('host')
            return FunctionWrapper(self.opts,
                                   id_,
                                   host,
                                   wfuncs=self.wfuncs,
                                   mods=self.mods,
                                   fsclient=self.fsclient,
                                   cmd_prefix=cmd,
                                   aliases=self.aliases,
                                   minion_opts=self.minion_opts,
                                   **kwargs)

        if self.cmd_prefix:
            # We're in an inner FunctionWrapper as created by the code block
            # above. Reconstruct the original cmd in the form 'cmd.run' and
            # then evaluate as normal
            cmd = '{0}.{1}'.format(self.cmd_prefix, cmd)

        if cmd in self.wfuncs:
            return self.wfuncs[cmd]

        if cmd in self.aliases:
            return self.aliases[cmd]

        def caller(*args, **kwargs):
            '''
            The remote execution function
            '''
            argv = [cmd]
            argv.extend([salt.utils.json.dumps(arg) for arg in args])
            argv.extend(
                ['{0}={1}'.format(salt.utils.stringutils.to_str(key),
                                  salt.utils.json.dumps(val))
                 for key, val in six.iteritems(kwargs)]
            )
            single = salt.client.ssh.Single(
                    self.opts,
                    argv,
                    mods=self.mods,
                    wipe=True,
                    fsclient=self.fsclient,
                    minion_opts=self.minion_opts,
                    **self.kwargs
            )
            stdout, stderr, retcode = single.cmd_block()
            if stderr.count('Permission Denied'):
                return {'_error': 'Permission Denied',
                        'stdout': stdout,
                        'stderr': stderr,
                        'retcode': retcode}
            try:
                ret = salt.utils.json.loads(stdout, object_hook=salt.utils.data.decode_dict)
                if len(ret) < 2 and 'local' in ret:
                    ret = ret['local']
                ret = ret.get('return', {})
            except ValueError:
                ret = {'_error': 'Failed to return clean data',
                       'stderr': stderr,
                       'stdout': stdout,
                       'retcode': retcode}
            return ret
        return caller