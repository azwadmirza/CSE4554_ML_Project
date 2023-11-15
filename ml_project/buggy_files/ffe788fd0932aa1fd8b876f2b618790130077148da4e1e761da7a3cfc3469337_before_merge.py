    def _open_channel(self, fw_host, fw_port, local_port):
        channel = self.session.direct_tcpip_ex(
            fw_host, fw_port, '127.0.0.1',
            local_port)
        while channel == LIBSSH2_ERROR_EAGAIN:
            self.poll()
            channel = self.session.direct_tcpip_ex(
                fw_host, fw_port, '127.0.0.1',
                local_port)
        return channel