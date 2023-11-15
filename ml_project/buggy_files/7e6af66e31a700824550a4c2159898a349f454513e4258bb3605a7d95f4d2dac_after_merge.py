    def get_status(self, filename):
        """Get kite status for a given filename."""
        success_status, kite_status = self._get_status(filename)
        if not filename or kite_status is None:
            kite_status = status()
            self.sig_status_response_ready[str].emit(kite_status)
        elif isinstance(kite_status, TEXT_TYPES):
            status_str = status(extra_status=' with errors')
            long_str = _("<code>{error}</code><br><br>"
                         "Note: If you are using a VPN, "
                         "please don't route requests to "
                         "localhost/127.0.0.1 with it").format(
                             error=kite_status)
            kite_status_dict = {
                'status': status_str,
                'short': status_str,
                'long': long_str}
            self.sig_status_response_ready[dict].emit(kite_status_dict)
        else:
            self.sig_status_response_ready[dict].emit(kite_status)