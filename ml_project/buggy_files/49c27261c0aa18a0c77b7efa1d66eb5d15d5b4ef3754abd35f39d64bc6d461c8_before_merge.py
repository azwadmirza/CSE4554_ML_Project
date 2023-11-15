    def list_remote_branches(self):
        sickbeard.GIT_REMOTE_BRANCHES = self.updater.list_remote_branches()
        return sickbeard.GIT_REMOTE_BRANCHES