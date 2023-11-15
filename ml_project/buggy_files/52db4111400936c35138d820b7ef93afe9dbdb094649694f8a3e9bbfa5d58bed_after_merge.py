    def send_command(self, command, prompt=None, answer=None, sendonly=False):
        """Executes a cli command and returns the results
        This method will execute the CLI command on the connection and return
        the results to the caller.  The command output will be returned as a
        string
        """
        kwargs = {'command': to_bytes(command), 'sendonly': sendonly}
        if prompt is not None:
            kwargs['prompt'] = to_bytes(prompt)
        if answer is not None:
            kwargs['answer'] = to_bytes(answer)

        if not signal.getsignal(signal.SIGALRM):
            signal.signal(signal.SIGALRM, self._alarm_handler)
        signal.alarm(self._connection._play_context.timeout)
        resp = self._connection.send(**kwargs)
        signal.alarm(0)
        return resp