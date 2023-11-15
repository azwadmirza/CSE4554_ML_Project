    def minimumTabSizeHint(self, index, ellipsis: bool = True) -> QSize:
        """Set the minimum tab size to indicator/icon/... text.

        Args:
            index: The index of the tab to get a size hint for.
            ellipsis: Whether to use ellipsis to calculate width
                      instead of the tab's text.
                      Forced to False for pinned tabs.
        Return:
            A QSize of the smallest tab size we can make.
        """
        icon = self.tabIcon(index)
        icon_padding = self.style().pixelMetric(PixelMetrics.icon_padding,
                                                None, self)
        if icon.isNull():
            icon_width = 0
        else:
            icon_width = min(icon.actualSize(self.iconSize()).width(),
                             self.iconSize().width()) + icon_padding

        pinned = self._tab_pinned(index)
        if not self.vertical and pinned and config.val.tabs.pinned.shrink:
            # Never consider ellipsis an option for horizontal pinned tabs
            ellipsis = False
        return self._minimum_tab_size_hint_helper(self.tabText(index),
                                                  icon_width, ellipsis,
                                                  pinned)