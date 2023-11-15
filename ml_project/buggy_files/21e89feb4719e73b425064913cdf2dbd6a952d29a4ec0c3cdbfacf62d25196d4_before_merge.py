    def restart_kernel(self):
        """Restart kernel of current client."""
        client = self.get_current_client()
        if self.test_no_stderr:
            stderr_file = None
        else:
            stderr_file = client.stderr_file

        if client is not None:
            stderr = self.get_stderr_file_handle(stderr_file)
            try:
                client.restart_kernel(stderr=stderr)
            finally:
                if stderr is not None:
                    stderr.close()