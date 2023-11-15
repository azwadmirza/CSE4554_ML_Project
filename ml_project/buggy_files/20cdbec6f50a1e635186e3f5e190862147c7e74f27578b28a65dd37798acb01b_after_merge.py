    def on_play_download_clicked(self):
        self.window().left_menu_button_video_player.click()
        if self.window().video_player_page.active_infohash != self.selected_item.download_info["infohash"]:
            self.window().video_player_page.play_media_item(self.selected_item.download_info["infohash"], -1)