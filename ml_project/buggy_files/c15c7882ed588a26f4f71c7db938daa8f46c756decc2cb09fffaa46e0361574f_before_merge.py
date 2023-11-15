    def on_torrent_status_updated(self, json_result, index):
        if not json_result:
            return

        if 'success' in json_result and json_result['success']:
            index.model().data_items[index.row()][u'status'] = json_result['new_status']

            self.window().edit_channel_page.channel_dirty = \
                self.table_view.window().edit_channel_page.channel_dirty or \
                (json_result['new_status'] != COMMIT_STATUS_COMMITTED)
            self.window().edit_channel_page.update_channel_commit_views(deleted_index=index)