    def do_CONNECT(self):
        # just provide a tunnel, transfer the data with no modification
        req = self
        req.path = "https://%s/" % req.path.replace(':443', '')

        u = urlsplit(req.path)
        address = (u.hostname, u.port or 443)
        try:
            conn = socket.create_connection(address)
        except socket.error as e:
            LOG.debug("HTTPConnectProxyHandler: Got exception while trying to connect to %s: %s" % (repr(address), e))
            self.send_error(504)  # 504 Gateway Timeout
            return
        self.send_response(200, 'Connection Established')
        self.send_header('Connection', 'close')
        self.end_headers()

        conns = [self.connection, conn]
        keep_connection = True
        while keep_connection:
            keep_connection = False
            rlist, wlist, xlist = select.select(conns, [], conns, self.timeout)
            if xlist:
                break
            for r in rlist:
                other = conns[1] if r is conns[0] else conns[0]
                data = r.recv(8192)
                if data:
                    other.sendall(data)
                    keep_connection = True
                    update_last_serve_time()
        conn.close()