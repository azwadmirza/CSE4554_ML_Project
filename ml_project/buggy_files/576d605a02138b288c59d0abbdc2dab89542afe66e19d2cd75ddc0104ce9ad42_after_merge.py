    def _send_cors_headers(self, response=None):
        headers = response and response.headers or {}
        if 'Access-Control-Allow-Origin' not in headers:
            self.send_header('Access-Control-Allow-Origin', '*')
        if 'Access-Control-Allow-Methods' not in headers:
            self.send_header('Access-Control-Allow-Methods', ','.join(CORS_ALLOWED_METHODS))
        if 'Access-Control-Allow-Headers' not in headers:
            requested_headers = self.headers.get('Access-Control-Request-Headers', '')
            requested_headers = re.split(r'[,\s]+', requested_headers) + CORS_ALLOWED_HEADERS
            self.send_header('Access-Control-Allow-Headers', ','.join([h for h in requested_headers if h]))
        if 'Access-Control-Expose-Headers' not in headers:
            self.send_header('Access-Control-Expose-Headers', ','.join(CORS_EXPOSE_HEADERS))