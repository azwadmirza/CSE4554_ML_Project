    def _get_urlencoded_form(self):
        is_valid_content_type = "application/x-www-form-urlencoded" in self.headers.get("content-type", "").lower()
        if is_valid_content_type:
            return tuple(mitmproxy.net.http.url.decode(self.get_text(strict=False)))
        return ()