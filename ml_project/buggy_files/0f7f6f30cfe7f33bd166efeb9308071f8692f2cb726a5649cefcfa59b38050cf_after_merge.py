    def on_play_request_done(self, result):
        if not self:
            return
        self.window().left_menu_button_video_player.click()
        self.window().video_player_page.play_media_item(self.torrent_info["infohash"], -1)