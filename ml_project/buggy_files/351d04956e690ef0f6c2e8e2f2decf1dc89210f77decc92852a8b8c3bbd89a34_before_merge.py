    def validate(self):
        """Pre-flight check for valid input and borg binary."""
        if self.is_remote_repo and not re.match(r'.+:.+', self.values['repo_url']):
            self._set_status(self.tr('Please enter a valid repo URL or select a local path.'))
            return False

        if self.__class__ == AddRepoWindow:
            if self.values['encryption'] != 'none':
                if len(self.values['password']) < 8:
                    self._set_status(self.tr('Please use a longer passphrase.'))
                    return False

        return True