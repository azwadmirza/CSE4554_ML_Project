    def on_received_metainfo(self, response):
        if not response or not self:
            return

        if 'error' in response:
            if response['error'] == 'metainfo error':
                # If it failed to load metainfo for max number of times, show an error message in red.
                if self.metainfo_retries > METAINFO_MAX_RETRIES:
                    self.dialog_widget.loading_files_label.setStyleSheet("color:#ff0000;")
                    self.dialog_widget.loading_files_label.setText("Failed to load files. Click to retry again.")
                    return
                self.perform_files_request()

            elif 'code' in response['error'] and response['error']['code'] == 'IOError':
                self.dialog_widget.loading_files_label.setText("Unable to read torrent file data")
            else:
                self.dialog_widget.loading_files_label.setText("Error: %s" % response['error'])
            return

        metainfo = json.loads(unhexlify(response['metainfo']))
        if 'files' in metainfo['info']:  # Multi-file torrent
            files = metainfo['info']['files']
        else:
            files = [{'path': [metainfo['info']['name']], 'length': metainfo['info']['length']}]

        # Show if the torrent already exists in the downloads
        if response.get('download_exists'):
            self.dialog_widget.existing_download_info_label.setText(
                "Note: this torrent already exists in the Downloads"
            )
        else:
            self.dialog_widget.existing_download_info_label.setText("")

        self.dialog_widget.files_list_view.clear()
        for filename in files:
            item = DownloadFileTreeWidgetItem(self.dialog_widget.files_list_view)
            item.setText(0, '/'.join(filename['path']))
            item.setText(1, format_size(float(filename['length'])))
            item.setData(0, Qt.UserRole, filename)
            item.setCheckState(2, Qt.Checked)
            self.dialog_widget.files_list_view.addTopLevelItem(item)

        self.has_metainfo = True
        self.dialog_widget.loading_files_label.setHidden(True)
        self.dialog_widget.download_files_container.setHidden(False)
        self.dialog_widget.files_list_view.setHidden(False)
        self.dialog_widget.adjustSize()
        self.on_main_window_resize()

        self.received_metainfo.emit(metainfo)