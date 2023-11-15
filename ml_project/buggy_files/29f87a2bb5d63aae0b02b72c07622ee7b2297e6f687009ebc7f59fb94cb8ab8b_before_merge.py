    def _resolve_buffer_index(self, index):
        """Resolve a buffer index to the tabbedbrowser and tab.

        Args:
            index: The [win_id/]index of the tab to be selected. Or a substring
                   in which case the closest match will be focused.
        """
        index_parts = index.split('/', 1)

        try:
            for part in index_parts:
                int(part)
        except ValueError:
            model = miscmodels.buffer()
            model.set_pattern(index)
            if model.count() > 0:
                index = model.data(model.first_item())
                index_parts = index.split('/', 1)
            else:
                raise cmdexc.CommandError(
                    "No matching tab for: {}".format(index))

        if len(index_parts) == 2:
            win_id = int(index_parts[0])
            idx = int(index_parts[1])
        elif len(index_parts) == 1:
            idx = int(index_parts[0])
            active_win = objreg.get('app').activeWindow()
            if active_win is None:
                # Not sure how you enter a command without an active window...
                raise cmdexc.CommandError(
                    "No window specified and couldn't find active window!")
            win_id = active_win.win_id

        if win_id not in objreg.window_registry:
            raise cmdexc.CommandError(
                "There's no window with id {}!".format(win_id))

        tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                    window=win_id)
        if not 0 < idx <= tabbed_browser.count():
            raise cmdexc.CommandError(
                "There's no tab with index {}!".format(idx))

        return (tabbed_browser, tabbed_browser.widget(idx-1))