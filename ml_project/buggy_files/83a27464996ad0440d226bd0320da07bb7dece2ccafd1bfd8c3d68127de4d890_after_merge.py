    def check_mining_directory(self):
        # Check that credit mining directory exists, if not try to re-create it.
        if not os.path.exists(self.settings.save_path):
            try:
                os.makedirs(self.settings.save_path)
                error_message = u"Credit mining directory [%s]  does not exist. Tribler will re-create the " \
                                u"directory and resume again.<br/>If you wish to disable credit mining entirely, " \
                                u"please go to Settings >> ANONYMITY >> Token mining. " % \
                                ensure_unicode(self.settings.save_path, 'utf-8')
            except OSError:
                self.shutdown()
                error_message = u"Credit mining directory [%s] was deleted or does not exist and Tribler could not " \
                                u"re-create the directory again. Credit mining will shutdown. Try restarting " \
                                u"Tribler. <br/>If you wish to disable credit mining entirely, please go to " \
                                u"Settings >> ANONYMITY >> Token mining. " % self.settings.save_path.encode('utf-8')

            gui_message = {"message": error_message}
            self.session.notifier.notify(NTFY_CREDIT_MINING, NTFY_ERROR, None, gui_message)
            return False
        return True