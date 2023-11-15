    def run(self):
        """Thread runner ensures a non main hub has been created for all subsequent
        greenlets and waits for (client, host, port) tuples to be put into self.in_q.

        A server is created once something is in the queue and the port to connect to
        is put into self.out_q.
        """
        self._hub = get_hub()
        assert self._hub.main_hub is False
        self.started.set()
        self._cleanup_let = spawn(self._cleanup_servers_let)
        logger.debug("Hub in server runner is main hub: %s", self._hub.main_hub)
        try:
            while True:
                if self.in_q.empty():
                    sleep(.01)
                    continue
                self._start_server()
        except Exception:
            logger.error("Tunnel thread caught exception and will exit:",
                         exc_info=1)
            self.shutdown()