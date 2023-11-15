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