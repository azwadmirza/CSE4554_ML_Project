    def write_to_stdin(self, line):
        """Send raw characters to the IPython kernel through stdin"""
        wait_loop = QEventLoop()
        self.sig_prompt_ready.connect(wait_loop.quit)
        self.kernel_client.input(line)
        wait_loop.exec_()

        # Remove loop connection and loop
        self.sig_prompt_ready.disconnect(wait_loop.quit)
        wait_loop = None

        # Run post exec commands
        self._post_exec_input(line)