    def _run_userscript(self, selection, cmd, args, verbose):
        """Run a userscript given as argument.

        Args:
            cmd: The userscript to run.
            args: Arguments to pass to the userscript.
            verbose: Show notifications when the command started/exited.
        """
        env = {
            'QUTE_MODE': 'command',
            'QUTE_SELECTED_TEXT': selection,
        }

        idx = self._current_index()
        if idx != -1:
            env['QUTE_TITLE'] = self._tabbed_browser.page_title(idx)

        # FIXME:qtwebengine: If tab is None, run_async will fail!
        tab = self._tabbed_browser.currentWidget()

        try:
            url = self._tabbed_browser.current_url()
        except qtutils.QtValueError:
            pass
        else:
            env['QUTE_URL'] = url.toString(QUrl.FullyEncoded)

        try:
            runner = userscripts.run_async(
                tab, cmd, *args, win_id=self._win_id, env=env, verbose=verbose)
        except userscripts.Error as e:
            raise cmdexc.CommandError(e)
        return runner