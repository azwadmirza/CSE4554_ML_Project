    def __call__(self):
        self.flow = WebSocketFlow(self.client_conn, self.server_conn, self.handshake_flow, self)
        self.flow.metadata['websocket_handshake'] = self.handshake_flow.id
        self.handshake_flow.metadata['websocket_flow'] = self.flow.id
        self.channel.ask("websocket_start", self.flow)

        client = self.client_conn.connection
        server = self.server_conn.connection
        conns = [client, server]
        close_received = False

        try:
            while not self.channel.should_exit.is_set():
                r = tcp.ssl_read_select(conns, 0.1)
                for conn in r:
                    source_conn = self.client_conn if conn == client else self.server_conn
                    other_conn = self.server_conn if conn == client else self.client_conn
                    is_server = (conn == self.server_conn.connection)

                    frame = websockets.Frame.from_file(source_conn.rfile)

                    cont = self._handle_frame(frame, source_conn, other_conn, is_server)
                    if not cont:
                        if close_received:
                            return
                        else:
                            close_received = True
        except (socket.error, exceptions.TcpException, SSL.Error) as e:
            s = 'server' if is_server else 'client'
            self.flow.error = flow.Error("WebSocket connection closed unexpectedly by {}: {}".format(s, repr(e)))
            self.channel.tell("websocket_error", self.flow)
        finally:
            self.channel.tell("websocket_end", self.flow)