    def murder_keepalived(self):
        now = time.time()
        while True:
            try:
                conn = self._keep.popleft()
            except IndexError:
                break

            delta = conn.timeout - now
            if delta > 0:
                self._keep.appendleft(conn)
                break
            else:
                # remove the connection from the queue
                conn = self._keep.popleft()

                # remove the socket from the poller
                self.poller.unregister(conn.sock)

                # close the socket
                util.close(conn.sock)