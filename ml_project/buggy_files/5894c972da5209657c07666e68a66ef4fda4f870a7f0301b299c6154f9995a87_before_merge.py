    def tab_move(self, index: typing.Union[str, int] = None, count=None):
        """Move the current tab according to the argument and [count].

        If neither is given, move it to the first position.

        Args:
            index: `+` or `-` to move relative to the current tab by
                   count, or a default of 1 space.
                   A tab index to move to that index.
            count: If moving relatively: Offset.
                   If moving absolutely: New position (default: 0). This
                   overrides the index argument, if given.
        """
        if index in ['+', '-']:
            # relative moving
            new_idx = self._current_index()
            delta = 1 if count is None else count
            if index == '-':
                new_idx -= delta
            elif index == '+':  # pragma: no branch
                new_idx += delta

            if config.val.tabs.wrap:
                new_idx %= self._count()
        else:
            # absolute moving
            if count is not None:
                new_idx = count - 1
            elif index is not None:
                new_idx = index - 1 if index >= 0 else index + self._count()
            else:
                new_idx = 0

        if not 0 <= new_idx < self._count():
            raise cmdexc.CommandError("Can't move tab to position {}!".format(
                new_idx + 1))

        cur_idx = self._current_index()
        cmdutils.check_overflow(cur_idx, 'int')
        cmdutils.check_overflow(new_idx, 'int')
        self._tabbed_browser.tabBar().moveTab(cur_idx, new_idx)