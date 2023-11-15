    def load(self, name, temp=False):
        """Load a named session.

        Args:
            name: The name of the session to load.
            temp: If given, don't set the current session.
        """
        path = self._get_session_path(name, check_exists=True)
        try:
            with open(path, encoding='utf-8') as f:
                data = utils.yaml_load(f)
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
            raise SessionError(e)

        log.sessions.debug("Loading session {} from {}...".format(name, path))
        for win in data['windows']:
            window = mainwindow.MainWindow(geometry=win['geometry'],
                                           private=win.get('private', None))
            window.show()
            tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                        window=window.win_id)
            tab_to_focus = None
            for i, tab in enumerate(win['tabs']):
                new_tab = tabbed_browser.tabopen(background=False)
                self._load_tab(new_tab, tab)
                if tab.get('active', False):
                    tab_to_focus = i
                if new_tab.data.pinned:
                    tabbed_browser.widget.set_tab_pinned(new_tab,
                                                         new_tab.data.pinned)
            if tab_to_focus is not None:
                tabbed_browser.widget.setCurrentIndex(tab_to_focus)
            if win.get('active', False):
                QTimer.singleShot(0, tabbed_browser.widget.activateWindow)

        if data['windows']:
            self.did_load = True
        if not name.startswith('_') and not temp:
            self._current = name