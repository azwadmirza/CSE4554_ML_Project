    def start(self, event=None, block=False):
        self._configure_loop()
        self._try_start_web_server()

        if not block:
            self._server_thread = threading.Thread(target=self._server.io_loop.start)
            self._server_thread.daemon = True
            self._server_thread.start()

            if event:
                event.set()
        else:
            if event:
                event.set()

            try:
                self._server.io_loop.start()
            except KeyboardInterrupt:
                pass