    def _commit_and_push(self):
        """ Commit all the files and push. """

        deploy = self._deploy_branch
        source = self._source_branch
        remote = self._remote_name

        source_commit = subprocess.check_output(['git', 'rev-parse', source])
        commit_message = (
            'Nikola auto commit.\n\n'
            'Source commit: %s'
            'Nikola version: %s' % (source_commit, __version__)
        )

        commands = [
            ['git', 'add', '-A'],
            ['git', 'commit', '-m', commit_message],
            ['git', 'push', '-f', remote, '%s:%s' % (deploy, deploy)],
            ['git', 'checkout', source],
        ]

        for command in commands:
            self.logger.info("==> {0}".format(command))
            try:
                subprocess.check_call(command)
            except subprocess.CalledProcessError as e:
                self.logger.error(
                    'Failed GitHub deployment — command {0} '
                    'returned {1}'.format(e.cmd, e.returncode)
                )
                sys.exit(e.returncode)