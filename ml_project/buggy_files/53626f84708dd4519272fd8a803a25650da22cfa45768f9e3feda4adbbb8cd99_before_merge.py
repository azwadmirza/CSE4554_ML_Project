    def set_page_title(self, idx, title):
        """Set the tab title user data."""
        self.tabBar().set_tab_data(idx, 'page-title', title)
        self._update_tab_title(idx)