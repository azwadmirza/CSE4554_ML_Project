    def initialize(self, identifier):
        self.channel_identifier = identifier
        self.window().manage_channel_create_torrent_back.setIcon(QIcon(get_image_path('page_back.png')))
        self.window().seed_after_adding_checkbox.setChecked(True)

        self.window().create_torrent_name_field.setText('')
        self.window().create_torrent_description_field.setText('')
        self.window().create_torrent_files_list.clear()
        self.window().create_torrent_files_list.customContextMenuRequested.connect(self.on_right_click_file_item)

        self.window().manage_channel_create_torrent_back.clicked.connect(self.on_create_torrent_manage_back_clicked)
        self.window().create_torrent_choose_files_button.clicked.connect(self.on_choose_files_clicked)
        self.window().create_torrent_choose_dir_button.clicked.connect(self.on_choose_dir_clicked)
        self.window().edit_channel_create_torrent_button.clicked.connect(self.on_create_clicked)