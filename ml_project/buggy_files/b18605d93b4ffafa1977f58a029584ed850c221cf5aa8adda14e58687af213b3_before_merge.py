    def connect_to_new_endpoint(self, force: bool = False):
        """Acquires a new WSS URL and tries to connect to the endpoint."""
        try:
            self.connect_operation_lock.acquire(blocking=True, timeout=5)
            if force or not self.is_connected():
                self.logger.info("Connecting to a new endpoint...")
                self.wss_uri = self.issue_new_wss_url()
                self.connect()
                self.logger.info("Connected to a new endpoint...")
        finally:
            self.connect_operation_lock.release()