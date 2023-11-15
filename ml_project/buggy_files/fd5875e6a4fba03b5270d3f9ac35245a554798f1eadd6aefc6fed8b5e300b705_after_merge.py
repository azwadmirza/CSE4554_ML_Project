    def _connect(self):
        '''
        Connect to a running IPCServer
        '''
        if isinstance(self.socket_path, int):
            sock_type = socket.AF_INET
            sock_addr = ('127.0.0.1', self.socket_path)
        else:
            sock_type = socket.AF_UNIX
            sock_addr = self.socket_path

        self.stream = IOStream(
            socket.socket(sock_type, socket.SOCK_STREAM),
            io_loop=self.io_loop,
        )
        while True:
            if self._closing:
                break
            try:
                log.trace('IPCClient: Connecting to socket: {0}'.format(self.socket_path))
                yield self.stream.connect(sock_addr)
                self._connecting_future.set_result(True)
                break
            except Exception as e:
                yield tornado.gen.sleep(1)  # TODO: backoff