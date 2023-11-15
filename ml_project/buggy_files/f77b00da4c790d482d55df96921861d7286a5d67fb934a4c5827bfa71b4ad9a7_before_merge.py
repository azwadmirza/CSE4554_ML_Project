    def initialize_player(self):
        vlc_available = True
        vlc = None
        try:
            from TriblerGUI import vlc
        except OSError:
            vlc_available = False

        if vlc and vlc.plugin_path:
            os.environ['VLC_PLUGIN_PATH'] = vlc.plugin_path

        if not vlc_available:
            # VLC is not available, we hide the video player button
            self.window().vlc_available = False
            self.window().left_menu_button_video_player.setHidden(True)
            return

        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.window().video_player_widget.should_hide_video_widgets.connect(self.hide_video_widgets)
        self.window().video_player_widget.should_show_video_widgets.connect(self.show_video_widgets)
        self.window().video_player_position_slider.should_change_video_position.connect(
            self.on_should_change_video_time)
        self.window().video_player_volume_slider.valueChanged.connect(self.on_volume_change)
        self.window().video_player_volume_slider.setValue(self.mediaplayer.audio_get_volume())
        self.window().video_player_volume_slider.setFixedWidth(0)

        self.window().video_player_play_pause_button.clicked.connect(self.on_play_pause_button_click)
        self.window().video_player_volume_button.clicked.connect(self.on_volume_button_click)
        self.window().video_player_full_screen_button.clicked.connect(self.on_full_screen_button_click)

        # Create play/pause and volume button images
        self.play_icon = QIcon(QPixmap(get_image_path("play.png")))
        self.pause_icon = QIcon(QPixmap(get_image_path("pause.png")))
        self.volume_on_icon = QIcon(QPixmap(get_image_path("volume_on.png")))
        self.volume_off_icon = QIcon(QPixmap(get_image_path("volume_off.png")))
        self.window().video_player_play_pause_button.setIcon(self.play_icon)
        self.window().video_player_volume_button.setIcon(self.volume_on_icon)
        self.window().video_player_full_screen_button.setIcon(QIcon(QPixmap(get_image_path("full_screen.png"))))
        self.window().video_player_info_button.setIcon(QIcon(QPixmap(get_image_path("info.png"))))
        self.window().video_player_info_button.hide()

        if sys.platform.startswith('linux'):
            self.mediaplayer.set_xwindow(self.window().video_player_widget.winId())
        elif sys.platform == "win32":
            self.mediaplayer.set_hwnd(self.window().video_player_widget.winId())
        elif sys.platform == "darwin":
            self.mediaplayer.set_nsobject(int(self.window().video_player_widget.winId()))

        self.manager = self.mediaplayer.event_manager()
        self.manager.event_attach(vlc.EventType.MediaPlayerBuffering, self.on_vlc_player_buffering)
        self.manager.event_attach(vlc.EventType.MediaPlayerPlaying, self.on_vlc_player_playing)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.on_update_timer_tick)
        self.update_timer.start(500)

        self.window().left_menu_playlist.playing_item_change.connect(self.change_playing_index)
        self.window().left_menu_playlist.item_should_play.connect(self.on_play_pause_button_click)
        self.window().left_menu_playlist.list_loaded.connect(self.on_files_list_loaded)
        self.window().video_player_play_pause_button.setEnabled(False)