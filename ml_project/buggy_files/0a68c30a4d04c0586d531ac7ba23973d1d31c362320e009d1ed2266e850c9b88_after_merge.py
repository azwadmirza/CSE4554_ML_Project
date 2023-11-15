    def _tab_close(self, tab, prev=False, next_=False, opposite=False):
        """Helper function for tab_close be able to handle message.async.

        Args:
            tab: Tab object to select be closed.
            prev: Force selecting the tab before the current tab.
            next_: Force selecting the tab after the current tab.
            opposite: Force selecting the tab in the opposite direction of
                      what's configured in 'tabs.select_on_remove'.
            count: The tab index to close, or None
        """
        tabbar = self._tabbed_browser.widget.tabBar()
        selection_override = self._get_selection_override(prev, next_,
                                                          opposite)

        if selection_override is None:
            self._tabbed_browser.close_tab(tab)
        else:
            old_selection_behavior = tabbar.selectionBehaviorOnRemove()
            tabbar.setSelectionBehaviorOnRemove(selection_override)
            self._tabbed_browser.close_tab(tab)
            tabbar.setSelectionBehaviorOnRemove(old_selection_behavior)