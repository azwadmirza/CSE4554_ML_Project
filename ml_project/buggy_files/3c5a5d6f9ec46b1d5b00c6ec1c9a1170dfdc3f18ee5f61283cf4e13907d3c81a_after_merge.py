    def on_should_change_video_time(self, position):
        if not self.mediaplayer or not self.media:
            return

        self.freeze = True
        self.mediaplayer.stop()
        self.mediaplayer.play()
        self.mediaplayer.set_position(position)

        # Guess the current position
        duration = self.media.get_duration() / 1000
        self.window().video_player_time_label.setText(f"{seconds_to_string(duration * position)} / "
                                                      f"{seconds_to_string(duration)}")