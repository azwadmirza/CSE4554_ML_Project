    def on_playlist_created(self, json_result):
        if 'created' in json_result and json_result['created']:
            self.on_playlist_edited_done()