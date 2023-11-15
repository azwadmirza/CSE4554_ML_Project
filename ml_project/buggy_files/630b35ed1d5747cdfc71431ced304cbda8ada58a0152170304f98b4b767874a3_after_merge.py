    def timer_callback(self):
        """
        Check for messages communicated from the web app, and update the GUI accordingly. Also,
        call ShareMode and ReceiveMode's timer_callbacks.
        """
        self.update()

        if not self.local_only:
            # Have we lost connection to Tor somehow?
            if not self.onion.is_authenticated():
                self.timer.stop()
                self.status_bar.showMessage(strings._('gui_tor_connection_lost'))
                self.system_tray.showMessage(strings._('gui_tor_connection_lost'), strings._('gui_tor_connection_error_settings'))

                self.share_mode.handle_tor_broke()
                self.receive_mode.handle_tor_broke()

        # Process events from the web object
        if self.mode == self.MODE_SHARE:
            mode = self.share_mode
        else:
            mode = self.receive_mode

        events = []

        done = False
        while not done:
            try:
                r = mode.web.q.get(False)
                events.append(r)
            except queue.Empty:
                done = True

        for event in events:
            if event["type"] == Web.REQUEST_LOAD:
                mode.handle_request_load(event)

            elif event["type"] == Web.REQUEST_STARTED:
                mode.handle_request_started(event)

            elif event["type"] == Web.REQUEST_RATE_LIMIT:
                mode.handle_request_rate_limit(event)

            elif event["type"] == Web.REQUEST_PROGRESS:
                mode.handle_request_progress(event)

            elif event["type"] == Web.REQUEST_CANCELED:
                mode.handle_request_canceled(event)

            elif event["type"] == Web.REQUEST_UPLOAD_FILE_RENAMED:
                mode.handle_request_upload_file_renamed(event)

            elif event["type"] == Web.REQUEST_UPLOAD_SET_DIR:
                mode.handle_request_upload_set_dir(event)

            elif event["type"] == Web.REQUEST_UPLOAD_FINISHED:
                mode.handle_request_upload_finished(event)

            elif event["type"] == Web.REQUEST_UPLOAD_CANCELED:
                mode.handle_request_upload_canceled(event)

            if event["type"] == Web.REQUEST_ERROR_DATA_DIR_CANNOT_CREATE:
                Alert(self.common, strings._('error_cannot_create_data_dir').format(event["data"]["receive_mode_dir"]))

            if event["type"] == Web.REQUEST_OTHER:
                if event["path"] != '/favicon.ico' and event["path"] != "/{}/shutdown".format(mode.web.shutdown_slug):
                    self.status_bar.showMessage('[#{0:d}] {1:s}: {2:s}'.format(mode.web.error404_count, strings._('other_page_loaded'), event["path"]))

        mode.timer_callback()