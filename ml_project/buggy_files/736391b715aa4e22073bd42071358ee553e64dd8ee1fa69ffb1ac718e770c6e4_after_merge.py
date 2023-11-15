    def perform_files_request(self):
        if self.closed:
            return

        direct = not self.dialog_widget.anon_download_checkbox.isChecked()
        request = f"torrentinfo?uri={quote_plus_unicode(self.download_uri)}"
        if direct is True:
            request = request + f"&hops=0"
        self.rest_request = TriblerNetworkRequest(request, self.on_received_metainfo, capture_core_errors=False)

        if self.metainfo_retries <= METAINFO_MAX_RETRIES:
            fetch_mode = 'directly' if direct else 'anonymously'
            loading_message = f"Loading torrent files {fetch_mode}..."
            timeout_message = (
                f"Timeout in fetching files {fetch_mode}. Retrying ({self.metainfo_retries}/{METAINFO_MAX_RETRIES})"
            )

            self.dialog_widget.loading_files_label.setText(
                loading_message if not self.metainfo_retries else timeout_message
            )
            self.metainfo_fetch_timer = QTimer()
            connect(self.metainfo_fetch_timer.timeout, self.perform_files_request)
            self.metainfo_fetch_timer.setSingleShot(True)
            self.metainfo_fetch_timer.start(METAINFO_TIMEOUT)

            self.metainfo_retries += 1