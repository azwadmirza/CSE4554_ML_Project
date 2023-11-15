    def initialize_with_playlists(self, playlists):
        if not playlists:
            return
        self.playlists_loaded.emit(playlists)
        self.playlists = playlists
        self.window().edit_channel_playlists_list.set_data_items([])

        self.update_playlist_list()

        viewing_playlist_index = self.get_index_of_viewing_playlist()
        if viewing_playlist_index != -1:
            self.viewing_playlist = self.playlists['playlists'][viewing_playlist_index]
            self.update_playlist_torrent_list()