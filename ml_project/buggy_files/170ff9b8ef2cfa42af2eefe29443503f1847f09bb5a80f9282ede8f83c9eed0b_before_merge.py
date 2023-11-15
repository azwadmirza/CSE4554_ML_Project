    def _get_status(self, filename):
        """Perform a request to get kite status for a file."""
        verb, url = KITE_ENDPOINTS.STATUS_ENDPOINT
        if filename:
            url_params = {'filename': filename}
        else:
            url_params = {'filetype': 'python'}
        success, response = self.perform_http_request(
            verb, url, url_params=url_params)
        return response