    def accept(self, listener):
        try:
            client, addr = listener.accept()
            # initialize the connection object
            conn = TConn(self.cfg, listener, client, addr)
            self.nr_conns += 1
            # enqueue the job
            self.enqueue_req(conn)
        except socket.error as e:
            if e.args[0] not in (errno.EAGAIN,
                    errno.ECONNABORTED, errno.EWOULDBLOCK):
                raise