    def _on_renderer_process_terminated(self, tab, status, code):
        """Show an error when a renderer process terminated."""
        if status == browsertab.TerminationStatus.normal:
            return

        messages = {
            browsertab.TerminationStatus.abnormal:
                "Renderer process exited with status {}".format(code),
            browsertab.TerminationStatus.crashed:
                "Renderer process crashed",
            browsertab.TerminationStatus.killed:
                "Renderer process was killed",
            browsertab.TerminationStatus.unknown:
                "Renderer process did not start",
        }
        msg = messages[status]

        def show_error_page(html):
            tab.set_html(html)
            log.webview.error(msg)

        if qtutils.version_check('5.9', compiled=False):
            url_string = tab.url(requested=True).toDisplayString()
            error_page = jinja.render(
                'error.html', title="Error loading {}".format(url_string),
                url=url_string, error=msg)
            QTimer.singleShot(100, lambda: show_error_page(error_page))
        else:
            # WORKAROUND for https://bugreports.qt.io/browse/QTBUG-58698
            message.error(msg)
            self._remove_tab(tab, crashed=True)
            if self.count() == 0:
                self.tabopen(QUrl('about:blank'))