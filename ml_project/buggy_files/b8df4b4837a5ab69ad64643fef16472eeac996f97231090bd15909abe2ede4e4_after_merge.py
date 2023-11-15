    def play_active_item(self):
        self.window().left_menu_playlist.set_active_index(self.active_index)
        file_info = self.window().left_menu_playlist.get_file_info(self.active_index)
        if file_info is None:
            return
        file_index = file_info["index"]

        self.window().video_player_header_label.setText(file_info["name"] if file_info else 'Unknown')

        # reset video player controls
        self.mediaplayer.stop()
        self.window().video_player_play_pause_button.setIcon(self.play_icon)
        self.window().video_player_position_slider.setValue(0)

        media_filename = u"http://127.0.0.1:" + unicode(self.video_player_port) + "/" + \
                         self.active_infohash + "/" + unicode(file_index)
        self.media = self.instance.media_new(media_filename)
        self.mediaplayer.set_media(self.media)
        self.media.parse()

        self.window().video_player_play_pause_button.setIcon(self.pause_icon)
        self.mediaplayer.play()

        self.window().video_player_play_pause_button.setEnabled(True)
        self.window().video_player_info_button.show()