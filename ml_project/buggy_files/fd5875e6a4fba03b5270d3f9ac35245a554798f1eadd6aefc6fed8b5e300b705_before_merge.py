    def _connect(self):
        '''
        Connect to a running IPCServer
        '''
        self.stream = IOStream(
            socket.socket(socket.AF_UNIX, socket.SOCK_STREAM),
            io_loop=self.io_loop,
        )
        while True:
            if self._closing:
                break
            try:
                log.trace('IPCClient: Connecting to socket: {0}'.format(self.socket_path))
                yield self.stream.connect(self.socket_path)
                self._connecting_future.set_result(True)
                break
            except Exception as e:
                yield tornado.gen.sleep(1)  # TODO: backoff