    def _run_check(self, low_data):
        '''
        Check that unless doesn't return 0, and that onlyif returns a 0.
        '''
        ret = {'result': False}
        cmd_opts = {}

        if 'shell' in self.opts['grains']:
            cmd_opts['shell'] = self.opts['grains'].get('shell')
        if 'onlyif' in low_data:
            if not isinstance(low_data['onlyif'], list):
                low_data_onlyif = [low_data['onlyif']]
            else:
                low_data_onlyif = low_data['onlyif']
            for entry in low_data_onlyif:
                if not isinstance(entry, string_types):
                    ret.update({'comment': 'onlyif execution failed, bad type passed', 'result': False})
                    return ret
                cmd = self.functions['cmd.retcode'](
                    entry, ignore_retcode=True, python_shell=True, **cmd_opts)
                log.debug('Last command return code: {0}'.format(cmd))
                if cmd != 0 and ret['result'] is False:
                    ret.update({'comment': 'onlyif execution failed',
                                'skip_watch': True,
                                'result': True})
                    return ret
                elif cmd == 0:
                    ret.update({'comment': 'onlyif execution succeeded', 'result': False})
            return ret

        if 'unless' in low_data:
            if not isinstance(low_data['unless'], list):
                low_data_unless = [low_data['unless']]
            else:
                low_data_unless = low_data['unless']
            for entry in low_data_unless:
                if not isinstance(entry, string_types):
                    ret.update({'comment': 'unless execution failed, bad type passed', 'result': False})
                    return ret
                cmd = self.functions['cmd.retcode'](
                    entry, ignore_retcode=True, python_shell=True, **cmd_opts)
                log.debug('Last command return code: {0}'.format(cmd))
                if cmd == 0 and ret['result'] is False:
                    ret.update({'comment': 'unless execution succeeded',
                                'skip_watch': True,
                                'result': True})
                elif cmd != 0:
                    ret.update({'comment': 'unless execution failed', 'result': False})
                    return ret

        # No reason to stop, return ret
        return ret