    def load_config(self, commands, commit=False, replace=False):
        """Loads the config commands onto the remote device
        """
        use_session = os.getenv('ANSIBLE_EOS_USE_SESSIONS', True)
        try:
            use_session = int(use_session)
        except ValueError:
            pass

        if not all((bool(use_session), self.supports_sessions)):
            if commit:
                return self.configure(self, commands)
            else:
                self._module.warn("EOS can not check config without config session")
                result = {'changed': True}
                return result

        conn = self._get_connection()
        session = 'ansible_%s' % int(time.time())
        result = {'session': session}

        out = conn.get('configure session %s' % session)

        if replace:
            out = conn.get('rollback clean-config')

        try:
            self.send_config(commands)
        except ConnectionError as exc:
            self.close_session(session)
            message = getattr(exc, 'err', exc)
            self._module.fail_json(msg="Error on executing commands %s" % commands, data=to_text(message, errors='surrogate_then_replace'))

        out = conn.get('show session-config diffs')
        if out:
            result['diff'] = to_text(out, errors='surrogate_then_replace').strip()

        if commit:
            conn.get('commit')
        else:
            self.close_session(session)

        return result