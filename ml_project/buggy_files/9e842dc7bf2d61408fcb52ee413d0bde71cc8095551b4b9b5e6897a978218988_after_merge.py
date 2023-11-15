    def on_torrent_info(self, torrent_info):
        if not torrent_info:
            return
        self.setTabEnabled(1, True)
        self.setTabEnabled(2, True)

        self.torrent_detail_files_list.clear()
        self.torrent_detail_trackers_list.clear()

        for file_info in torrent_info["files"]:
            item = QTreeWidgetItem(self.torrent_detail_files_list)
            item.setText(0, file_info["path"])
            item.setText(1, format_size(float(file_info["size"])))

        for tracker in torrent_info["trackers"]:
            if tracker == 'DHT':
                continue
            item = QTreeWidgetItem(self.torrent_detail_trackers_list)
            item.setText(0, tracker)

        if torrent_info["num_seeders"] > 0:
            self.torrent_detail_health_label.setText("good health (S%d L%d)" % (torrent_info["num_seeders"],
                                                                                torrent_info["num_leechers"]))
        elif torrent_info["num_leechers"] > 0:
            self.torrent_detail_health_label.setText("unknown health (found peers)")
        else:
            self.torrent_detail_health_label.setText("no peers found")