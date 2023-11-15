    def comm_channel_manager(self, comm_id, queue_message=False):
        """Use comm_channel instead of shell_channel."""
        if queue_message:
            # Send without comm_channel
            yield
            return

        if not self.comm_channel_connected():
            # Ask again for comm config
            self.remote_call()._send_comm_config()
            timeout = 45
            self._wait(self.comm_channel_connected,
                       self._sig_channel_open,
                       "Timeout while waiting for comm port.",
                       timeout)

        id_list = self.get_comm_id_list(comm_id)
        for comm_id in id_list:
            self._comms[comm_id]['comm']._send_channel = (
                self.kernel_client.comm_channel)
        try:
            yield
        finally:
            for comm_id in id_list:
                self._comms[comm_id]['comm']._send_channel = (
                    self.kernel_client.shell_channel)