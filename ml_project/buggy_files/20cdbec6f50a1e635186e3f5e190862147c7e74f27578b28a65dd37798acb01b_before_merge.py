    def on_play_download_clicked(self):
        self.window().left_menu_button_video_player.click()
        self.window().video_player_page.set_torrent_infohash(self.selected_item.download_info["infohash"])
        self.window().left_menu_playlist.set_loading()