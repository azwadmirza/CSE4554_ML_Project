    def clean_url(self) -> str:
        """Sanitized repo URL (with removed HTTP Basic Auth)"""
        url = yarl.URL(self.url)
        try:
            return url.with_user(None).human_repr()
        except ValueError:
            return self.url