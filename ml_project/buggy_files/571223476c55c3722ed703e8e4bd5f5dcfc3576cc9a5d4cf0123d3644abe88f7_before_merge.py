    def _exit_if_output_committed(self):
        """ Exit if the output folder is committed on the source branch. """

        source = self._source_branch
        subprocess.check_call(['git', 'checkout', source])

        output_folder = self.site.config['OUTPUT_FOLDER']
        output_log = subprocess.check_output(
            ['git', 'ls-files', '--', output_folder]
        )

        if len(output_log.strip()) > 0:
            self.logger.error(
                'Output folder is committed on the source branch. '
                'Cannot proceed until it is removed.'
            )
            sys.exit(1)