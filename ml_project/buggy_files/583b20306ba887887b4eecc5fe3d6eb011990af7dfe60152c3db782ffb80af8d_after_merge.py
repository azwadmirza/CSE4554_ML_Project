    def tabSizeHint(self, index: int):
        """Override tabSizeHint to customize qb's tab size.

        https://wiki.python.org/moin/PyQt/Customising%20tab%20bars

        Args:
            index: The index of the tab.

        Return:
            A QSize.
        """
        if self.count() == 0:
            # This happens on startup on macOS.
            # We return it directly rather than setting `size' because we don't
            # want to ensure it's valid in this special case.
            return QSize()

        minimum_size = self.minimumTabSizeHint(index)
        height = minimum_size.height()
        if self.vertical:
            confwidth = str(config.val.tabs.width)
            if confwidth.endswith('%'):
                main_window = objreg.get('main-window', scope='window',
                                         window=self._win_id)
                perc = int(confwidth.rstrip('%'))
                width = main_window.width() * perc / 100
            else:
                width = int(confwidth)
            size = QSize(max(minimum_size.width(), width), height)
        else:
            if config.val.tabs.pinned.shrink:
                pinned = self._tab_pinned(index)
                pinned_count, pinned_width = self._pinned_statistics()
            else:
                pinned = False
                pinned_count, pinned_width = 0, 0
            no_pinned_count = self.count() - pinned_count
            no_pinned_width = self.width() - pinned_width

            if pinned:
                # Give pinned tabs the minimum size they need to display their
                # titles, let Qt handle scaling it down if we get too small.
                width = self.minimumTabSizeHint(index, ellipsis=False).width()
            else:
                width = no_pinned_width / no_pinned_count

            # If no_pinned_width is not divisible by no_pinned_count, add a
            # pixel to some tabs so that there is no ugly leftover space.
            if (no_pinned_count > 0 and
                    index < no_pinned_width % no_pinned_count):
                width += 1

            # If we don't have enough space, we return the minimum size so we
            # get scroll buttons as soon as needed.
            width = max(width, minimum_size.width())

            size = QSize(width, height)
        qtutils.ensure_valid(size)
        return size