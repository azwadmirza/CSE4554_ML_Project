    def load_config(self, config, commit=False, replace=False):
        """Loads the configuration onto the remote devices

        If the device doesn't support configuration sessions, this will
        fallback to using configure() to load the commands.  If that happens,
        there will be no returned diff or session values
        """
        use_session = os.getenv('ANSIBLE_EOS_USE_SESSIONS', True)
        try:
            use_session = int(use_session)
        except ValueError:
            pass

        if not all((bool(use_session), self.supports_sessions)):
            if commit:
                return self.configure(config)
            else:
                self._module.warn("EOS can not check config without config session")
                result = {'changed': True}
                return result

        session = 'ansible_%s' % int(time.time())
        result = {'session': session}
        commands = ['configure session %s' % session]

        if replace:
            commands.append('rollback clean-config')

        commands.extend(config)

        response = self.send_request(commands)
        if 'error' in response:
            commands = ['configure session %s' % session, 'abort']
            self.send_request(commands)
            err = response['error']
            self._module.fail_json(msg=err['message'], code=err['code'])

        commands = ['configure session %s' % session, 'show session-config diffs']
        if commit:
            commands.append('commit')
        else:
            commands.append('abort')

        response = self.send_request(commands, output='text')
        diff = response['result'][1]['output']
        if len(diff) > 0:
            result['diff'] = diff

        return result