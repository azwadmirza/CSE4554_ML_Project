    def _connect_signals(self):
        """Connect all mainwindow signals."""
        status = self._get_object('statusbar')
        keyparsers = self._get_object('keyparsers')
        completion_obj = self._get_object('completion')
        cmd = self._get_object('status-command')
        message_bridge = self._get_object('message-bridge')
        mode_manager = self._get_object('mode-manager')

        # misc
        self.tabbed_browser.close_window.connect(self.close)
        mode_manager.entered.connect(hints.on_mode_entered)

        # status bar
        mode_manager.entered.connect(status.on_mode_entered)
        mode_manager.left.connect(status.on_mode_left)
        mode_manager.left.connect(cmd.on_mode_left)
        mode_manager.left.connect(message.global_bridge.mode_left)

        # commands
        keyparsers[usertypes.KeyMode.normal].keystring_updated.connect(
            status.keystring.setText)
        cmd.got_cmd[str].connect(self._commandrunner.run_safely)
        cmd.got_cmd[str, int].connect(self._commandrunner.run_safely)
        cmd.returnPressed.connect(self.tabbed_browser.on_cmd_return_pressed)

        # key hint popup
        for mode, parser in keyparsers.items():
            parser.keystring_updated.connect(functools.partial(
                self._keyhint.update_keyhint, mode.name))

        # messages
        message.global_bridge.show_message.connect(
            self._messageview.show_message)
        message.global_bridge.flush()
        message.global_bridge.clear_messages.connect(
            self._messageview.clear_messages)

        message_bridge.s_set_text.connect(status.set_text)
        message_bridge.s_maybe_reset_text.connect(status.txt.maybe_reset_text)

        # statusbar
        self.tabbed_browser.current_tab_changed.connect(status.on_tab_changed)

        self.tabbed_browser.cur_progress.connect(status.prog.setValue)
        self.tabbed_browser.cur_load_finished.connect(status.prog.hide)
        self.tabbed_browser.cur_load_started.connect(
            status.prog.on_load_started)

        self.tabbed_browser.cur_scroll_perc_changed.connect(
            status.percentage.set_perc)
        self.tabbed_browser.tab_index_changed.connect(
            status.tabindex.on_tab_index_changed)

        self.tabbed_browser.cur_url_changed.connect(status.url.set_url)
        self.tabbed_browser.cur_url_changed.connect(functools.partial(
            status.backforward.on_tab_cur_url_changed,
            tabs=self.tabbed_browser))
        self.tabbed_browser.cur_link_hovered.connect(status.url.set_hover_url)
        self.tabbed_browser.cur_load_status_changed.connect(
            status.url.on_load_status_changed)
        self.tabbed_browser.cur_fullscreen_requested.connect(
            self._on_fullscreen_requested)
        self.tabbed_browser.cur_fullscreen_requested.connect(status.maybe_hide)

        # command input / completion
        mode_manager.left.connect(self.tabbed_browser.on_mode_left)
        cmd.clear_completion_selection.connect(
            completion_obj.on_clear_completion_selection)
        cmd.hide_completion.connect(completion_obj.hide)