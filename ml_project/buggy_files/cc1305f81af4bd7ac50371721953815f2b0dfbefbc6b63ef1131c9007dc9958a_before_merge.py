    def received_playlists_in_channel(self, results):
        for result in results['playlists']:
            self.playlists.append((PlaylistListItem, result))
        self.loaded_playlists = True
        self.update_result_list()