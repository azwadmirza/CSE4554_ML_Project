    def _ensure_git_repo(self):
        """ Ensure that the site is a git-repo.

        Also make sure that a remote with the specified name exists.

        """

        try:
            remotes = subprocess.check_output(['git', 'remote'])
        except subprocess.CalledProcessError as e:
            self.logger.notice('github_deploy needs a git repository!')
            sys.exit(e.returncode)
        except OSError as e:
            import errno
            self.logger.error('Running git failed with {0}'.format(e))
            if e.errno == errno.ENOENT:
                self.logger.notice('Is git on the PATH?')
            sys.exit(1)
        else:
            if self._remote_name not in remotes:
                self.logger.error(
                    'Need a remote called "%s" configured' % self._remote_name
                )
                sys.exit(1)