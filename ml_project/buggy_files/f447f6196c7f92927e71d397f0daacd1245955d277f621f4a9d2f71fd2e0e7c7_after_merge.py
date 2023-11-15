    def _run_extra_scripts(self, ep_obj):
        """
        Execute any extra scripts defined in the config.

        :param ep_obj: The object to use when calling the extra script
        """
        if not app.EXTRA_SCRIPTS:
            return

        ep_location = ep_obj.location
        file_path = self.file_path
        indexer_id = str(ep_obj.series.indexerid)
        season = str(ep_obj.season)
        episode = str(ep_obj.episode)
        airdate = str(ep_obj.airdate)

        for cur_script_name in app.EXTRA_SCRIPTS:

            # generate a safe command line string to execute the script and provide all the parameters
            script_cmd = [piece for piece in cur_script_name.split(' ') if piece.strip()]
            self.log(u'Running extra script: {0}'.format(cur_script_name), logger.INFO)

            script_cmd += [ep_location, file_path, indexer_id, season, episode, airdate]
            # use subprocess to run the command and capture output
            self.log(u'Executing command: {0}'.format(script_cmd))
            try:
                process = subprocess.Popen(
                    script_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=app.PROG_DIR
                )
                out, _ = process.communicate()

                self.log(u'Script result: {0}'.format(out), logger.DEBUG)

            except Exception as error:
                self.log(u'Unable to run extra script: {0!r}'.format(error))