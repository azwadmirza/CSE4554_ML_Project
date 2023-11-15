    def murder_keepalived(self):
        now = time.time()
        while True:
            try:
                # remove the connection from the queue
                conn = self._keep.popleft()
            except IndexError:
                break

            delta = conn.timeout - now
            if delta > 0:
                # add the connection back to the queue
                self._keep.appendleft(conn)
                break
            else:
                # remove the socket from the poller
                self.poller.unregister(conn.sock)

                # close the socket
                util.close(conn.sock)