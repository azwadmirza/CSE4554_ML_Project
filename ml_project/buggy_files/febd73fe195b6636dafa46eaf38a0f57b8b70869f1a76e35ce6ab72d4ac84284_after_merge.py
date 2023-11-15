    def _send_command(self, command, raw_text=False, cmd_verify=True):
        """
        Wrapper for Netmiko's send_command method.

        raw_text argument is not used and is for code sharing with NX-API.
        """
        return self.device.send_command(command, cmd_verify=cmd_verify)