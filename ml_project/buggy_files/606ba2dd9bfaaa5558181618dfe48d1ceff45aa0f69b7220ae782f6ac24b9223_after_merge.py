    def __init__(self, parent, download_uri):
        DialogContainer.__init__(self, parent)

        torrent_name = download_uri
        if torrent_name.startswith('file:'):
            torrent_name = torrent_name[5:]
        elif torrent_name.startswith('magnet:'):
            torrent_name = unquote_plus(torrent_name)

        self.download_uri = download_uri
        self.has_metainfo = False
        gui_settings = self.window().gui_settings

        uic.loadUi(get_ui_file_path('startdownloaddialog.ui'), self.dialog_widget)

        self.dialog_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.dialog_widget.browse_dir_button.clicked.connect(self.on_browse_dir_clicked)
        self.dialog_widget.cancel_button.clicked.connect(lambda: self.button_clicked.emit(0))
        self.dialog_widget.download_button.clicked.connect(self.on_download_clicked)
        self.dialog_widget.select_all_files_button.clicked.connect(self.on_all_files_selected_clicked)
        self.dialog_widget.deselect_all_files_button.clicked.connect(self.on_all_files_deselected_clicked)

        self.dialog_widget.destination_input.setStyleSheet("""
        QComboBox {
            background-color: #444;
            border: none;
            color: #C0C0C0;
            padding: 4px;
        }
        QComboBox::drop-down {
            width: 20px;
            border: 1px solid #999;
            border-radius: 2px;
        }
        QComboBox QAbstractItemView {
            selection-background-color: #707070;
            color: #C0C0C0;
        }
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
            image: url('%s');
        }
        """ % get_image_path('down_arrow_input.png'))

        if self.window().tribler_settings:
            # Set the most recent download locations in the QComboBox
            current_settings = get_gui_setting(self.window().gui_settings, "recent_download_locations", "")
            if len(current_settings) > 0:
                recent_locations = [url.decode('hex').decode('utf-8') for url in current_settings.split(",")]
                self.dialog_widget.destination_input.addItems(recent_locations)
            else:
                self.dialog_widget.destination_input.setCurrentText(
                    self.window().tribler_settings['downloadconfig']['saveas'])

        self.dialog_widget.torrent_name_label.setText(torrent_name)

        self.dialog_widget.anon_download_checkbox.stateChanged.connect(self.on_anon_download_state_changed)
        self.dialog_widget.safe_seed_checkbox.setChecked(get_gui_setting(gui_settings, "default_safeseeding_enabled",
                                                                         True, is_bool=True))
        self.dialog_widget.anon_download_checkbox.setChecked(get_gui_setting(gui_settings, "default_anonymity_enabled",
                                                                             True, is_bool=True))

        self.dialog_widget.safe_seed_checkbox.setEnabled(self.dialog_widget.anon_download_checkbox.isChecked())

        self.perform_files_request()
        self.dialog_widget.files_list_view.setHidden(True)
        self.dialog_widget.download_files_container.setHidden(True)
        self.dialog_widget.adjustSize()
        self.on_anon_download_state_changed(None)

        self.on_main_window_resize()