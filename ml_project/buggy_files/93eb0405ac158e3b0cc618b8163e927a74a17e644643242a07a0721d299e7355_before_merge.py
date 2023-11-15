    def on_received_downloads(self, downloads):
        if not downloads:
            return  # This might happen when closing Tribler

        total_download = 0
        total_upload = 0
        self.received_downloads.emit(downloads)
        self.downloads = downloads

        download_infohashes = set()

        items = []
        for download in downloads["downloads"]:
            if download["infohash"] in self.download_widgets:
                item = self.download_widgets[download["infohash"]]
            else:
                item = DownloadWidgetItem()
                self.download_widgets[download["infohash"]] = item
                items.append(item)

            item.update_with_download(download)

            # Update video player with download info
            video_infohash = self.window().video_player_page.active_infohash
            if video_infohash != "" and download["infohash"] == video_infohash:
                self.window().video_player_page.update_with_download_info(download)

            total_download += download["speed_down"]
            total_upload += download["speed_up"]

            download_infohashes.add(download["infohash"])

            if self.window().download_details_widget.current_download is not None and \
                    self.window().download_details_widget.current_download["infohash"] == download["infohash"]:
                self.window().download_details_widget.current_download = download
                self.window().download_details_widget.update_pages()

        self.window().downloads_list.addTopLevelItems(items)
        for item in items:
            self.window().downloads_list.setItemWidget(item, 2, item.bar_container)

        # Check whether there are download that should be removed
        for infohash, item in self.download_widgets.items():
            if infohash not in download_infohashes:
                index = self.window().downloads_list.indexOfTopLevelItem(item)
                self.window().downloads_list.takeTopLevelItem(index)
                del self.download_widgets[infohash]

        if self.window().tray_icon:
            self.window().tray_icon.setToolTip(
                "Down: %s, Up: %s" % (format_speed(total_download), format_speed(total_upload)))
        self.update_download_visibility()
        self.schedule_downloads_timer()

        # Update the top download management button if we have a row selected
        if len(self.window().downloads_list.selectedItems()) > 0:
            self.on_download_item_clicked()