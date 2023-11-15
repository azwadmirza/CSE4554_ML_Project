    def clean_url(self):
        """Sanitized repo URL (with removed HTTP Basic Auth)"""
        url = yarl.URL(self.url)
        clean_url = url.with_user(None)
        return clean_url