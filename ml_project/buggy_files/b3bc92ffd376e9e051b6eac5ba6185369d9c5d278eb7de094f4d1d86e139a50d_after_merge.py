    def _do_close(self):
        """Helper function for closeEvent."""
        try:
            last_visible = objreg.get('last-visible-main-window')
            if self is last_visible:
                objreg.delete('last-visible-main-window')
        except KeyError:
            pass
        sessions.session_manager.save_last_window_session()
        self._save_geometry()
        log.destroy.debug("Closing window {}".format(self.win_id))