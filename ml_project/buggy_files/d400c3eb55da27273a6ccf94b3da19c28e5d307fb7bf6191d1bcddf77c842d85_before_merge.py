    def closeEvent(self, e):
        """Override closeEvent to display a confirmation if needed."""
        if crashsignal.is_crashing:
            e.accept()
            return
        tab_count = self.tabbed_browser.count()
        download_model = objreg.get('download-model', scope='window',
                                    window=self.win_id)
        download_count = download_model.running_downloads()
        quit_texts = []
        # Ask if multiple-tabs are open
        if 'multiple-tabs' in config.val.confirm_quit and tab_count > 1:
            quit_texts.append("{} {} open.".format(
                tab_count, "tab is" if tab_count == 1 else "tabs are"))
        # Ask if multiple downloads running
        if 'downloads' in config.val.confirm_quit and download_count > 0:
            quit_texts.append("{} {} running.".format(
                download_count,
                "download is" if download_count == 1 else "downloads are"))
        # Process all quit messages that user must confirm
        if quit_texts or 'always' in config.val.confirm_quit:
            msg = jinja.environment.from_string("""
                <ul>
                {% for text in quit_texts %}
                   <li>{{text}}</li>
                {% endfor %}
                </ul>
            """.strip()).render(quit_texts=quit_texts)
            confirmed = message.ask('Really quit?', msg,
                                    mode=usertypes.PromptMode.yesno,
                                    default=True)

            # Stop asking if the user cancels
            if not confirmed:
                log.destroy.debug("Cancelling closing of window {}".format(
                    self.win_id))
                e.ignore()
                return
        e.accept()
        self._do_close()