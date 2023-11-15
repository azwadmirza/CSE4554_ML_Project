    def _open_channel(self, fw_host, fw_port, local_port):
        channel = self.session.direct_tcpip_ex(
            fw_host, fw_port, self.bind_address,
            local_port)
        while channel == LIBSSH2_ERROR_EAGAIN:
            self._client.poll()
            channel = self.session.direct_tcpip_ex(
                fw_host, fw_port, self.bind_address,
                local_port)
        return channel