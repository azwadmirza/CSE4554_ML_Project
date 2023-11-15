    def _connect_tab_signals(self, tab):
        """Set up the needed signals for tab."""
        # filtered signals
        tab.link_hovered.connect(
            self._filter.create(self.cur_link_hovered, tab))
        tab.load_progress.connect(
            self._filter.create(self.cur_progress, tab))
        tab.load_finished.connect(
            self._filter.create(self.cur_load_finished, tab))
        tab.load_started.connect(
            self._filter.create(self.cur_load_started, tab))
        tab.scroller.perc_changed.connect(
            self._filter.create(self.cur_scroll_perc_changed, tab))
        tab.url_changed.connect(
            self._filter.create(self.cur_url_changed, tab))
        tab.load_status_changed.connect(
            self._filter.create(self.cur_load_status_changed, tab))
        tab.fullscreen_requested.connect(
            self._filter.create(self.cur_fullscreen_requested, tab))
        tab.caret.selection_toggled.connect(
            self._filter.create(self.cur_caret_selection_toggled, tab))
        # misc
        tab.scroller.perc_changed.connect(self.on_scroll_pos_changed)
        tab.url_changed.connect(
            functools.partial(self.on_url_changed, tab))
        tab.title_changed.connect(
            functools.partial(self.on_title_changed, tab))
        tab.icon_changed.connect(
            functools.partial(self.on_icon_changed, tab))
        tab.load_progress.connect(
            functools.partial(self.on_load_progress, tab))
        tab.load_finished.connect(
            functools.partial(self.on_load_finished, tab))
        tab.load_started.connect(
            functools.partial(self.on_load_started, tab))
        tab.window_close_requested.connect(
            functools.partial(self.on_window_close_requested, tab))
        tab.renderer_process_terminated.connect(
            functools.partial(self._on_renderer_process_terminated, tab))
        tab.new_tab_requested.connect(self.tabopen)
        if not self.private:
            web_history = objreg.get('web-history')
            tab.add_history_item.connect(web_history.add_from_tab)