    def reset_player(self):
        """
        Reset the video player, i.e. when a download is removed that was being played.
        """
        self.active_infohash = ""
        self.active_index = -1
        self.window().left_menu_playlist.clear()
        self.window().video_player_header_label.setText("")
        self.mediaplayer.stop()
        self.mediaplayer.set_media(None)
        self.media = None
        self.window().video_player_play_pause_button.setIcon(self.play_icon)
        self.window().video_player_play_pause_button.setEnabled(False)
        self.window().video_player_position_slider.setValue(0)
        self.window().video_player_info_button.hide()