    def clean(self):
        """Call git clean to remove all untracked files.

        It only affects source folders (sickbeard, sickrage) and the lib folder,
        to prevent deleting untracked user data not known by .gitignore

        :return:
        :rtype: bool
        """
        for folder in ('lib', 'sickbeard', 'sickrage'):
            _, _, exit_status = self._run_git(self._git_path, 'clean -d -f {0}'.format(folder))
            if exit_status != 0:
                return False

        return True