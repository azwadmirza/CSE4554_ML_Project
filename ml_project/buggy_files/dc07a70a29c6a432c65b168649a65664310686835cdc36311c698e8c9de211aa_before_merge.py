    def _handle_input_request(self, msg):
        """
        Reimplemented to be able to handle requests when we ask for
        hidden inputs
        """
        self.kernel_client.iopub_channel.flush()
        if not self._hidden:
            def callback(line):
                self.kernel_client.input(line)
            if self._reading:
                self._reading = False
            self._readline(msg['content']['prompt'], callback=callback,
                           password=msg['content']['password'])
        else:
            # This is what we added, i.e. not doing anything if
            # Spyder asks for silent inputs
            pass