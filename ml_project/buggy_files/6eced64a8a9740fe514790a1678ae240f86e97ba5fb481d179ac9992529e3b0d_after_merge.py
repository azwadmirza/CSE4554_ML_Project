    def set_tab_pinned(self, tab: QWidget,
                       pinned: bool) -> None:
        """Set the tab status as pinned.

        Args:
            tab: The tab to pin
            pinned: Pinned tab state to set.
        """
        bar = self.tabBar()
        idx = self.indexOf(tab)

        bar.set_tab_data(idx, 'pinned', pinned)
        tab.data.pinned = pinned
        self.update_tab_favicon(tab)
        self.update_tab_title(idx)