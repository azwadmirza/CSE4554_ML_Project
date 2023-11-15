    def update_channel_commit_views(self, reload_view=False):
        if self.channel_dirty and self.autocommit_enabled:
            self.commit_timer.stop()
            self.commit_timer.start(CHANNEL_COMMIT_DELAY)
            if reload_view:
                self.load_my_torrents()

        self.window().commit_control_bar.setHidden(not self.channel_dirty or self.autocommit_enabled)