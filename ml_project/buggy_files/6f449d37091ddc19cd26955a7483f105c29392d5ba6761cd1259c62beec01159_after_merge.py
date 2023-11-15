    def write_to_stdin(self, line):
        """Send raw characters to the IPython kernel through stdin"""
        self._control.insert_text(line + '\n')
        self._reading = False
        self.kernel_client.input(line)