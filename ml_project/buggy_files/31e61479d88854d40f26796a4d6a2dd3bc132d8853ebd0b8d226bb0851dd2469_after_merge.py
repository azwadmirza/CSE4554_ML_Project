    def _on_load_finished(self, ok):
        """Display a static error page if JavaScript is disabled."""
        super()._on_load_finished(ok)
        js_enabled = self.settings.test_attribute('content.javascript.enabled')
        if not ok and not js_enabled:
            self.dump_async(self._error_page_workaround)

        if ok and self._reload_url is not None:
            # WORKAROUND for https://bugreports.qt.io/browse/QTBUG-66656
            log.config.debug(
                "Loading {} again because of config change".format(
                    self._reload_url.toDisplayString()))
            QTimer.singleShot(100, lambda url=self._reload_url:
                              self.openurl(url, predict=False))
            self._reload_url = None

        if not qtutils.version_check('5.10', compiled=False):
            # We can't do this when we have the loadFinished workaround as that
            # sometimes clears icons without loading a new page.
            # In general, this is handled by Qt, but when loading takes long,
            # the old icon is still displayed.
            self.icon_changed.emit(QIcon())