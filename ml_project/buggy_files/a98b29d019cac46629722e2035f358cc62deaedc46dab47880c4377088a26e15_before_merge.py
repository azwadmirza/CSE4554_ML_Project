    def savvy_settings(self):
        if not self._savvy_settings:
            self._savvy_settings = GitSavvySettings(self)
        return self._savvy_settings