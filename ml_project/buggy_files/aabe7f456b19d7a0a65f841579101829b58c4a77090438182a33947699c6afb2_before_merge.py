    def update_pages(self, new_download=False):
        if self.current_download is None:
            return

        self.window().download_progress_bar.update_with_download(self.current_download)
        self.window().download_detail_name_label.setText(self.current_download['name'])
        self.window().download_detail_status_label.setText(DLSTATUS_STRINGS[eval(self.current_download["status"])])
        self.window().download_detail_filesize_label.setText("%s in %d files" %
                                                             (format_size(float(self.current_download["size"])),
                                                              len(self.current_download["files"])))
        self.window().download_detail_health_label.setText("%d seeders, %d leechers" %
                                                           (self.current_download["num_seeds"],
                                                            self.current_download["num_peers"]))
        self.window().download_detail_infohash_label.setText(self.current_download['infohash'])
        self.window().download_detail_destination_label.setText(self.current_download["destination"])
        self.window().download_detail_availability_label.setText("%.2f" % self.current_download['availability'])

        if new_download:  # When we have a new download, clear all pages and draw new widgets

            # Populate the files list
            self.window().download_files_list.clear()
            self.files_widgets = {}
            for dfile in self.current_download["files"]:
                item = QTreeWidgetItem(self.window().download_files_list)
                DownloadsDetailsTabWidget.update_file_row(item, dfile)
                self.files_widgets[dfile["name"]] = item

        else:  # No new download, just update data in the lists
            for dfile in self.current_download["files"]:
                DownloadsDetailsTabWidget.update_file_row(self.files_widgets[dfile["name"]], dfile)

        # Populate the trackers list
        self.window().download_trackers_list.clear()
        for tracker in self.current_download["trackers"]:
            item = QTreeWidgetItem(self.window().download_trackers_list)
            DownloadsDetailsTabWidget.update_tracker_row(item, tracker)
            self.tracker_widgets[tracker["url"]] = item

        # Populate the peers list if the peer information is available
        self.window().download_peers_list.clear()
        if "peers" in self.current_download:
            for peer in self.current_download["peers"]:
                item = QTreeWidgetItem(self.window().download_peers_list)
                DownloadsDetailsTabWidget.update_peer_row(item, peer)