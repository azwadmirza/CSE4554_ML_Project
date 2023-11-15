    def get_tcp_dstip(self, sock):
        pfile = self.firewall.pfile

        try:
            peer = sock.getpeername()
        except socket.error:
            _, e = sys.exc_info()[:2]
            if e.args[0] == errno.EINVAL:
                return sock.getsockname()

        proxy = sock.getsockname()

        argv = (sock.family, socket.IPPROTO_TCP,
                peer[0].encode("ASCII"), peer[1],
                proxy[0].encode("ASCII"), proxy[1])
        out_line = b"QUERY_PF_NAT %d,%d,%s,%d,%s,%d\n" % argv
        pfile.write(out_line)
        pfile.flush()
        in_line = pfile.readline()
        debug2(out_line.decode("ASCII") + ' > ' + in_line.decode("ASCII"))
        if in_line.startswith(b'QUERY_PF_NAT_SUCCESS '):
            (ip, port) = in_line[21:].split(b',')
            return (ip.decode("ASCII"), int(port))

        return sock.getsockname()