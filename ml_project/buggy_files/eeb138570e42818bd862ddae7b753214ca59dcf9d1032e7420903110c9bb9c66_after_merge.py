    def _set_urlencoded_form(self, form_data):
        """
        Sets the body to the URL-encoded form data, and adds the appropriate content-type header.
        This will overwrite the existing content if there is one.
        """
        self.headers["content-type"] = "application/x-www-form-urlencoded"
        self.content = mitmproxy.net.http.url.encode(form_data, self.get_text(strict=False)).encode()