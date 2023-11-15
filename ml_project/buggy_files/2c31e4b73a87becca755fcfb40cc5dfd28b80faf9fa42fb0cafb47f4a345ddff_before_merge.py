    def tabRemoved(self, idx):
        """Update titles when a tab was removed."""
        super().tabRemoved(idx)
        self._update_tab_titles()