    def update_with_torrent(self, torrent):
        if not torrent:
            return
        self.show_torrent = True
        self.torrent_info = torrent
        self.thumbnail_widget.initialize(torrent["name"], HOME_ITEM_FONT_SIZE)
        self.main_label.setText(torrent["name"])
        self.category_label.setText(torrent["category"].lower() if
                                    ("category" in torrent and torrent["category"]) else 'other')
        self.category_label.adjustSize()
        self.category_label.setHidden(False)
        self.setCursor(Qt.ArrowCursor)
        self.detail_label.setText("Size: " + format_size(torrent["size"]))