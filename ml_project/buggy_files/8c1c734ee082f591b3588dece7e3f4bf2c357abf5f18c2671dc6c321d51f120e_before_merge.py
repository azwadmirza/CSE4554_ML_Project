    def on_play_file(self, file_info):
        self.window().left_menu_button_video_player.click()
        self.window().video_player_page.set_torrent_infohash(self.current_download["infohash"])
        self.window().video_player_page.change_playing_index(file_info["index"], file_info["name"])
        self.window().left_menu_playlist.set_files(self.current_download["files"])
        self.window().left_menu_playlist.set_active_index(file_info["index"])