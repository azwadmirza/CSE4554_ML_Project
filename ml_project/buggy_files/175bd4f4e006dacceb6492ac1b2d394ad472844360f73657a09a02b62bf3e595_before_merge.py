    def run(self):
        self.mode.common.log('OnionThread', 'run')

        try:
            self.mode.app.start_onion_service()
            self.success.emit()

        except (TorTooOld, TorErrorInvalidSetting, TorErrorAutomatic, TorErrorSocketPort, TorErrorSocketFile, TorErrorMissingPassword, TorErrorUnreadableCookieFile, TorErrorAuthError, TorErrorProtocolError, BundledTorTimeout, OSError) as e:
            self.error.emit(e.args[0])
            return

        self.mode.app.stay_open = not self.mode.common.settings.get('close_after_first_download')

        # start onionshare http service in new thread
        self.mode.web_thread = WebThread(self.mode)
        self.mode.web_thread.start()

        # wait for modules in thread to load, preventing a thread-related cx_Freeze crash
        time.sleep(0.2)