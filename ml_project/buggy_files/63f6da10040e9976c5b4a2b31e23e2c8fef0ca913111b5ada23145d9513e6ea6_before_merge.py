    def change_playing_index(self, index, filename):
        self.active_index = index
        self.window().video_player_header_label.setText(filename)

        # reset video player controls
        self.mediaplayer.stop()
        self.window().video_player_play_pause_button.setIcon(self.play_icon)
        self.window().video_player_position_slider.setValue(0)

        media_filename = u"http://127.0.0.1:" + unicode(self.video_player_port) + "/" + \
                         self.active_infohash + "/" + unicode(index)
        self.media = self.instance.media_new(media_filename)
        self.mediaplayer.set_media(self.media)
        self.media.parse()

        self.window().video_player_play_pause_button.setIcon(self.pause_icon)
        self.mediaplayer.play()

        self.window().video_player_play_pause_button.setEnabled(True)
        self.window().video_player_info_button.show()