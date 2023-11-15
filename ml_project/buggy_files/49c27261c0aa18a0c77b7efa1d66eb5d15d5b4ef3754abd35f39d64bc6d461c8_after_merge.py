    def list_remote_branches(self):
        if self.updater:
            sickbeard.GIT_REMOTE_BRANCHES = self.updater.list_remote_branches()
        return sickbeard.GIT_REMOTE_BRANCHES