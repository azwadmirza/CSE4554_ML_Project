    def _save_all(self, *, only_window=None, with_private=False):
        """Get a dict with data for all windows/tabs."""
        data = {'windows': []}
        if only_window is not None:
            winlist = [only_window]
        else:
            winlist = objreg.window_registry

        for win_id in sorted(winlist):
            tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                        window=win_id)
            main_window = objreg.get('main-window', scope='window',
                                     window=win_id)

            # We could be in the middle of destroying a window here
            if sip.isdeleted(main_window):
                continue

            if tabbed_browser.private and not with_private:
                continue

            win_data = {}
            active_window = QApplication.instance().activeWindow()
            if getattr(active_window, 'win_id', None) == win_id:
                win_data['active'] = True
            win_data['geometry'] = bytes(main_window.saveGeometry())
            win_data['tabs'] = []
            if tabbed_browser.private:
                win_data['private'] = True
            for i, tab in enumerate(tabbed_browser.widgets()):
                active = i == tabbed_browser.widget.currentIndex()
                win_data['tabs'].append(self._save_tab(tab, active))
            data['windows'].append(win_data)
        return data