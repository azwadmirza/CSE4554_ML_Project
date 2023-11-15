    def start(self):
        '''
        Perform the work necessary to start up a Tornado IPC server

        Blocks until socket is established

        :param str/int socket_path: Path on the filesystem for the
                                    socket to bind to. This socket does
                                    not need to exist prior to calling
                                    this method, but parent directories
                                    should.
                                    It may also be of type 'int', in
                                    which case it is used as the port
                                    for a tcp localhost connection.
        '''
        # Start up the ioloop
        log.trace('IPCServer: binding to socket: {0}'.format(self.socket_path))
        if isinstance(self.socket_path, int):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(0)
            self.sock.bind(('127.0.0.1', self.socket_path))
            self.sock.listen(128)
        else:
            self.sock = tornado.netutil.bind_unix_socket(self.socket_path)

        tornado.netutil.add_accept_handler(
            self.sock,
            self.handle_connection,
            io_loop=self.io_loop,
        )
        self._started = True