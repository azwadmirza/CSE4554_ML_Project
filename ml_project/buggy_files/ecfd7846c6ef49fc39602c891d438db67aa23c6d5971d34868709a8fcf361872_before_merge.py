    def start(self):
        '''
        Perform the work necessary to start up a Tornado IPC server

        Blocks until socket is established

        :param str socket_path: Path on the filesystem for the socket to bind to.
                                This socket does not need to exist prior to calling
                                this method, but parent directories should.
        '''
        # Start up the ioloop
        log.trace('IPCServer: binding to socket: {0}'.format(self.socket_path))
        self.sock = tornado.netutil.bind_unix_socket(self.socket_path)

        tornado.netutil.add_accept_handler(
            self.sock,
            self.handle_connection,
            io_loop=self.io_loop,
        )
        self._started = True