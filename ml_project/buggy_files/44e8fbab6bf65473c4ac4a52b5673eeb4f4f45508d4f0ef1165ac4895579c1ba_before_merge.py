    def post_fork(self, payload_handler, io_loop):
        '''
        After forking we need to create all of the local sockets to listen to the
        router

        :param func payload_handler: A function to called to handle incoming payloads as
                                     they are picked up off the wire
        :param IOLoop io_loop: An instance of a Tornado IOLoop, to handle event scheduling
        '''
        self.payload_handler = payload_handler
        self.io_loop = io_loop

        self.context = zmq.Context(1)
        self._socket = self.context.socket(zmq.REP)
        if self.opts.get('ipc_mode', '') == 'tcp':
            self.w_uri = 'tcp://127.0.0.1:{0}'.format(
                self.opts.get('tcp_master_workers', 4515)
                )
        else:
            self.w_uri = 'ipc://{0}'.format(
                os.path.join(self.opts['sock_dir'], 'workers.ipc')
                )
        log.info('Worker binding to socket {0}'.format(self.w_uri))
        self._socket.connect(self.w_uri)

        salt.transport.mixins.auth.AESReqServerMixin.post_fork(self, payload_handler, io_loop)

        self.stream = zmq.eventloop.zmqstream.ZMQStream(self._socket, io_loop=self.io_loop)
        self.stream.on_recv_stream(self.handle_message)