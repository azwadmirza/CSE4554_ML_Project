    def send(self, command, prompt=None, answer=None, newline=True, sendonly=False):
        '''
        Sends the command to the device in the opened shell
        '''
        try:
            self._history.append(command)
            self._ssh_shell.sendall(b'%s\r' % command)
            if sendonly:
                return
            response = self.receive(command, prompt, answer, newline)
            return to_text(response, errors='surrogate_or_strict')
        except (socket.timeout, AttributeError):
            display.vvvv(traceback.format_exc(), host=self._play_context.remote_addr)
            raise AnsibleConnectionFailure("timeout trying to send command: %s" % command.strip())