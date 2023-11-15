    def get_status(self, filename):
        """Get kite status for a given filename."""
        kite_status = self._get_status(filename)
        if not filename or kite_status is None:
            kite_status = status()
            self.sig_status_response_ready[str].emit(kite_status)
        else:
            self.sig_status_response_ready[dict].emit(kite_status)