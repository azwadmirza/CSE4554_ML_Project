    def _start_cb(self, elems):
        """Initialize the elements and labels based on the context set."""
        if self._context is None:
            log.hints.debug("In _start_cb without context!")
            return

        if not elems:
            message.error("No elements found.")
            return

        # Because _start_cb is called asynchronously, it's possible that the
        # user switched to another tab or closed the tab/window. In that case
        # we should not start hinting.
        tabbed_browser = objreg.get('tabbed-browser', default=None,
                                    scope='window', window=self._win_id)
        tab = tabbed_browser.widget.currentWidget()
        if tab.tab_id != self._tab_id:
            log.hints.debug(
                "Current tab changed ({} -> {}) before _start_cb is run."
                .format(self._tab_id, tab.tab_id))
            return

        strings = self._hint_strings(elems)
        log.hints.debug("hints: {}".format(', '.join(strings)))

        for elem, string in zip(elems, strings):
            label = HintLabel(elem, self._context)
            label.update_text('', string)
            self._context.all_labels.append(label)
            self._context.labels[string] = label

        keyparsers = objreg.get('keyparsers', scope='window',
                                window=self._win_id)
        keyparser = keyparsers[usertypes.KeyMode.hint]
        keyparser.update_bindings(strings)

        message_bridge = objreg.get('message-bridge', scope='window',
                                    window=self._win_id)
        message_bridge.set_text(self._get_text())
        modeman.enter(self._win_id, usertypes.KeyMode.hint,
                      'HintManager.start')

        if self._context.first:
            self._fire(strings[0])
            return
        # to make auto_follow == 'always' work
        self._handle_auto_follow()