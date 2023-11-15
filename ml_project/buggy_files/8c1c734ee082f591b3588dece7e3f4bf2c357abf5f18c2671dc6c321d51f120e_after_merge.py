    def on_play_file(self, file_info):
        self.window().left_menu_button_video_player.click()
        self.window().video_player_page.play_media_item(self.current_download["infohash"], file_info["index"])