    def accept(self, listener):
        try:
            client, addr = listener.accept()
            # initialize the connection object
            conn = TConn(self.cfg, listener, client, addr)
            self.nr_conns += 1
            # enqueue the job
            self.enqueue_req(conn)
        except EnvironmentError as e:
            if e.errno not in (errno.EAGAIN,
                    errno.ECONNABORTED, errno.EWOULDBLOCK):
                raise