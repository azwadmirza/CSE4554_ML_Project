    def update(self):
        """
        Calls git pull origin <branch> in order to update SickRage. Returns a bool depending
        on the call's success.
        """

        # update remote origin url
        self.update_remote_origin()

        # remove untracked files and performs a hard reset on git branch to avoid update issues
        if self._is_hard_reset_allowed():
            # self.clean() # This is removing user data and backups
            self.reset()

        if self.branch == self._find_installed_branch():
            _, _, exit_status = self._run_git(self._git_path, 'pull -f %s %s' % (sickbeard.GIT_REMOTE, self.branch))  # @UnusedVariable
        else:
            _, _, exit_status = self._run_git(self._git_path, 'checkout -f ' + self.branch)  # @UnusedVariable

        if exit_status == 0:
            self._find_installed_version()
            # Notify update successful
            if sickbeard.NOTIFY_ON_UPDATE:
                try:
                    notifiers.notify_git_update(sickbeard.CUR_COMMIT_HASH or "")
                except Exception:
                    logger.log(u"Unable to send update notification. Continuing the update process", logger.DEBUG)
            return True

        else:
            return False