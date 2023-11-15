    def do_action(self, commit_hash, **kwargs):
        self.git("cherry-pick", commit_hash)
        self.view.window().status_message("Commit %s cherry-picked successfully." % commit_hash)
        util.view.refresh_gitsavvy(self.window.active_view())