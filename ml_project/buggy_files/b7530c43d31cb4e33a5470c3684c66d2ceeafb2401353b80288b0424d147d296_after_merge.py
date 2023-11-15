    def on_exception(self, *exc_info):
        if self.tray_icon:
            self.tray_icon.deleteLater()

        # Stop the download loop
        self.downloads_page.stop_loading_downloads()

        # Add info about whether we are stopping Tribler or not
        os.environ['TRIBLER_SHUTTING_DOWN'] = str(self.core_manager.shutting_down)

        if not self.core_manager.shutting_down:
            self.core_manager.stop(stop_app_on_shutdown=False)

        self.setHidden(True)

        if self.debug_window:
            self.debug_window.setHidden(True)

        exception_text = "".join(traceback.format_exception(*exc_info))
        logging.error(exception_text)

        if not self.feedback_dialog_is_open:
            dialog = FeedbackDialog(self, exception_text, self.core_manager.events_manager.tribler_version,
                                    self.start_time)
            self.feedback_dialog_is_open = True
            _ = dialog.exec_()