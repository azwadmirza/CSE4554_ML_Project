    def connect(self, url):
        if not url.startswith("file:"):
            self.request_url = url
            self._create_connection()
            self._store_response()
            self.conn.close()
        else:
            self.status_code = StatusCode(200, 'Ok')