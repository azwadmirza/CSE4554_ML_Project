    def _set_current_index(self, idx):
        """Convenience method to set the current widget index."""
        cmdutils.check_overflow(idx, 'int')
        self._tabbed_browser.setCurrentIndex(idx)