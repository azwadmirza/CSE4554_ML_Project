    def run(self):
        self.should_exit.clear()
        self.server.start_slave(Slave, Channel(self.masterq, self.should_exit))
        while not self.should_exit.is_set():

            # Don't choose a very small timeout in Python 2:
            # https://github.com/mitmproxy/mitmproxy/issues/443
            # TODO: Lower the timeout value if we move to Python 3.
            self.tick(self.masterq, 0.1)
        self.shutdown()