    def restart_kernel(self):
        """Restart kernel of current client."""
        client = self.get_current_client()

        if client is not None:
            client.restart_kernel()