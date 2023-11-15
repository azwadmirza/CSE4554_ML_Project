    def on_playlist_edited(self, json_result):
        if not json_result:
            return
        if 'modified' in json_result and json_result['modified']:
            self.on_playlist_edited_done()