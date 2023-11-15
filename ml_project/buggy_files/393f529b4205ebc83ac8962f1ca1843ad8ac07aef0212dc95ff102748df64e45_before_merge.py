    def on_received_metainfo(self, metainfo):
        if not metainfo:
            return

        if 'error' in metainfo:
            if metainfo['error'] == 'timeout':
                self.dialog_widget.loading_files_label.setText("Timeout when trying to fetch files.")
            elif 'code' in metainfo['error'] and metainfo['error']['code'] == 'IOError':
                self.dialog_widget.loading_files_label.setText("Unable to read torrent file data")
            else:
                self.dialog_widget.loading_files_label.setText("Error: %s" % metainfo['error'])
            return

        metainfo = metainfo['metainfo']
        if 'files' in metainfo['info']:  # Multi-file torrent
            files = metainfo['info']['files']
        else:
            files = [{'path': [metainfo['info']['name']], 'length': metainfo['info']['length']}]

        # Show if the torrent already exists in the downloads
        if 'download_exists' in metainfo and metainfo['download_exists']:
            self.dialog_widget.existing_download_info_label.setText("Note: this torrent already exists in the Downloads")
        else:
            self.dialog_widget.existing_download_info_label.setText("")

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