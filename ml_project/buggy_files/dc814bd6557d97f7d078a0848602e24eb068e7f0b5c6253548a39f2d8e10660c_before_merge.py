    def tabInserted(self, idx):
        """Update titles when a tab was inserted."""
        super().tabInserted(idx)
        self._update_tab_titles()