    def on_remove_download_dialog(self, action):
        if action != 2:
            for selected_item in self.selected_items:
                infohash = selected_item.download_info["infohash"]

                # Reset video player if necessary before doing the actual request
                if self.window().video_player_page.active_infohash == infohash:
                    self.window().video_player_page.reset_player()

                TriblerNetworkRequest(
                    "downloads/%s" % infohash, self.on_download_removed, method='DELETE',
                    data={"remove_data": bool(action)}
                )
        if self.dialog:
            self.dialog.close_dialog()
            self.dialog = None