    def update_channel_commit_views(self, deleted_index=None):
        if self.channel_dirty and self.autocommit_enabled:
            self.commit_timer.stop()
            self.commit_timer.start(CHANNEL_COMMIT_DELAY)
            if deleted_index:
                # TODO: instead of reloading the whole table, just remove the deleted row and update start and end
                self.load_my_torrents()

        self.window().commit_control_bar.setHidden(not self.channel_dirty or self.autocommit_enabled)