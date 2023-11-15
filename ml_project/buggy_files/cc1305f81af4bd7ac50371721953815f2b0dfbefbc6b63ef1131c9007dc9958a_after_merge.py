    def received_playlists_in_channel(self, results):
        if not results:
            return
        for result in results['playlists']:
            self.playlists.append((PlaylistListItem, result))
        self.loaded_playlists = True
        self.update_result_list()