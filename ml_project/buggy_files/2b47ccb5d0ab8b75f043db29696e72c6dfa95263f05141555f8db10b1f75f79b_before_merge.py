    def _on_load_finished(self, ok):
        sess_manager = objreg.get('session-manager')
        sess_manager.save_autosave()

        if ok and not self._has_ssl_errors:
            if self.url().scheme() == 'https':
                self._set_load_status(usertypes.LoadStatus.success_https)
            else:
                self._set_load_status(usertypes.LoadStatus.success)
        elif ok:
            self._set_load_status(usertypes.LoadStatus.warn)
        else:
            self._set_load_status(usertypes.LoadStatus.error)
        self.load_finished.emit(ok)
        if not self.title():
            self.title_changed.emit(self.url().toDisplayString())

        self.zoom.set_current()