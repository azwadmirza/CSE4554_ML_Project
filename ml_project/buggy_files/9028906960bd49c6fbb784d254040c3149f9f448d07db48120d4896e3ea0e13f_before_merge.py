    def __init__(self, parent, torrent, show_controls=False, on_remove_clicked=None):
        QWidget.__init__(self, parent)
        fc_channel_torrent_list_item.__init__(self)

        self.torrent_info = torrent

        self.setupUi(self)
        self.show_controls = show_controls
        self.remove_control_button_container.setHidden(True)
        self.control_buttons_container.setHidden(True)
        self.is_health_checking = False
        self.has_health = False
        self.health_request_mgr = None
        self.request_mgr = None
        self.download_uri = None
        self.dialog = None

        self.channel_torrent_name.setText(torrent["name"])
        if torrent["size"] is None:
            self.channel_torrent_description.setText("Size: -")
        else:
            self.channel_torrent_description.setText("Size: %s" % format_size(float(torrent["size"])))

        if torrent["category"]:
            self.channel_torrent_category.setText(torrent["category"].lower())
        else:
            self.channel_torrent_category.setText("unknown")
        self.thumbnail_widget.initialize(torrent["name"], 24)

        if torrent["last_tracker_check"] > 0:
            self.has_health = True
            self.update_health(int(torrent["num_seeders"]), int(torrent["num_leechers"]))

        self.torrent_play_button.clicked.connect(self.on_play_button_clicked)
        self.torrent_download_button.clicked.connect(self.on_download_clicked)

        if not self.window().vlc_available:
            self.torrent_play_button.setHidden(True)

        if on_remove_clicked is not None:
            self.remove_torrent_button.clicked.connect(lambda: on_remove_clicked(self))