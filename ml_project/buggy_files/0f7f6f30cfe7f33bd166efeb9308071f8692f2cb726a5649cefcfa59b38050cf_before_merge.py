    def on_play_request_done(self, result):
        if not self:
            return
        self.window().left_menu_button_video_player.click()
        self.window().video_player_page.set_torrent_infohash(self.torrent_info["infohash"])
        self.window().left_menu_playlist.set_loading()