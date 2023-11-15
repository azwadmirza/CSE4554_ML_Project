    def _on_predicted_navigation(self, url):
        """If we know we're going to visit an URL soon, change the settings."""
        self.settings.update_for_url(url)