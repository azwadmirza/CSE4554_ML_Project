    def run(self):
        try:
            self._init_tunnel_client()
            self._init_tunnel_sock()
        except Exception as ex:
            logger.error("Tunnel initilisation failed with %s", ex)
            self.exception = ex
            return
        logger.debug("Hub in run function: %s", get_hub())
        try:
            while True:
                logger.debug("Tunnel waiting for connection")
                self.tunnel_open.set()
                self.forward_sock, forward_addr = self.socket.accept()
                logger.debug("Client connected, forwarding %s:%s on"
                             " remote host to local %s",
                             self.fw_host, self.fw_port,
                             forward_addr)
                self.session.set_blocking(1)
                self.channel = self.session.direct_tcpip_ex(
                    self.fw_host, self.fw_port, '127.0.0.1', forward_addr[1])
                if self.channel is None:
                    self.forward_sock.close()
                    self.socket.close()
                    raise Exception("Could not establish channel to %s:%s",
                                    self.fw_host, self.fw_port)
                self.session.set_blocking(0)
                source = spawn(self._read_forward_sock)
                dest = spawn(self._read_channel)
                joinall((source, dest))
                self.channel.close()
                self.forward_sock.close()
        finally:
            if not self.socket.closed:
                self.socket.close()