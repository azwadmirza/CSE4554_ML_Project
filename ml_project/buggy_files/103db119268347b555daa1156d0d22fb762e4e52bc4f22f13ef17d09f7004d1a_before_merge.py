    def update_with_download_info(self, download):
        if len(download["files"]) > 0 and not self.window().left_menu_playlist.loaded_list:
            self.window().left_menu_playlist.set_files(download["files"])

            # Play the video with the largest file index
            largest_file = None

            for file_info in download["files"]:
                if is_video_file(file_info["name"]) and (largest_file is None or
                                                         file_info["size"] > largest_file["size"]):
                    largest_file = file_info

            if not largest_file:
                # We don't have a media file in this torrent. Reset everything and show an error
                ConfirmationDialog.show_error(self.window(), "No media files", "This download contains no media files.")
                self.window().hide_left_menu_playlist()
                return

            self.window().left_menu_playlist.set_active_index(largest_file["index"])
            self.change_playing_index(largest_file["index"], largest_file["name"])

        self.window().video_player_info_button.popup.update(download)