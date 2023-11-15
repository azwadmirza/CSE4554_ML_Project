    def _filter_signals(self, signal, tab, *args):
        """Filter signals and trigger TabbedBrowser signals if needed.

        Triggers signal if the original signal was sent from the _current_ tab
        and not from any other one.

        The original signal does not matter, since we get the new signal and
        all args.

        Args:
            signal: The signal to emit if the sender was the current widget.
            tab: The WebView which the filter belongs to.
            *args: The args to pass to the signal.
        """
        log_signal = debug.signal_name(signal) not in self.BLACKLIST
        tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                    window=self._win_id)
        try:
            tabidx = tabbed_browser.widget.indexOf(tab)
        except RuntimeError:
            # The tab has been deleted already
            return
        if tabidx == tabbed_browser.widget.currentIndex():
            if log_signal:
                log.signals.debug("emitting: {} (tab {})".format(
                    debug.dbg_signal(signal, args), tabidx))
            signal.emit(*args)
        else:
            if log_signal:
                log.signals.debug("ignoring: {} (tab {})".format(
                    debug.dbg_signal(signal, args), tabidx))