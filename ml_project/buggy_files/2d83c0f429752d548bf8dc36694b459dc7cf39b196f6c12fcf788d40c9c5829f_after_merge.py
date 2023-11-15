    def request_folding(self):
        """Request folding."""
        if not self.folding_supported or not self.code_folding:
            return
        params = {'file': self.filename}
        return params