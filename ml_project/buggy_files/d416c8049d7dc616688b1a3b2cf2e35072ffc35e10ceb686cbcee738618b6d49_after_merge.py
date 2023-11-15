    def eventFilter(self, obj, event):
        """Act on ChildAdded events."""
        if event.type() == QEvent.ChildAdded:
            child = event.child()
            log.mouse.debug("{} got new child {}, installing filter".format(
                obj, child))
            assert obj is self._widget
            child.installEventFilter(self._filter)

            if qtutils.version_check('5.11', compiled=False, exact=True):
                # WORKAROUND for https://bugreports.qt.io/browse/QTBUG-68076
                pass_modes = [usertypes.KeyMode.command,
                              usertypes.KeyMode.prompt,
                              usertypes.KeyMode.yesno]
                if modeman.instance(self._win_id).mode not in pass_modes:
                    tabbed_browser = objreg.get('tabbed-browser',
                                                scope='window',
                                                window=self._win_id)
                    current_index = tabbed_browser.widget.currentIndex()
                    try:
                        widget_index = tabbed_browser.widget.indexOf(
                            self._widget.parent())
                    except RuntimeError:
                        widget_index = -1
                    if current_index == widget_index:
                        QTimer.singleShot(0, self._widget.setFocus)

        elif event.type() == QEvent.ChildRemoved:
            child = event.child()
            log.mouse.debug("{}: removed child {}".format(obj, child))

        return False