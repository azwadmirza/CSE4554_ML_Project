    def _run_extra_scripts(self, ep_obj):
        """
        Execute any extra scripts defined in the config.

        :param ep_obj: The object to use when calling the extra script
        """
        if not app.EXTRA_SCRIPTS:
            return

        def _attempt_to_encode(item, _encoding):
            if isinstance(item, text_type):
                try:
                    item = item.encode(_encoding)
                except UnicodeEncodeError:
                    pass  # ignore it
                finally:
                    return item

        encoding = app.SYS_ENCODING

        file_path = _attempt_to_encode(self.file_path, encoding)
        ep_location = _attempt_to_encode(ep_obj.location, encoding)
        indexer_id = str(ep_obj.series.indexerid)
        season = str(ep_obj.season)
        episode = str(ep_obj.episode)
        airdate = str(ep_obj.airdate)

        for cur_script_name in app.EXTRA_SCRIPTS:
            cur_script_name = _attempt_to_encode(cur_script_name, encoding)

            # generate a safe command line string to execute the script and provide all the parameters
            script_cmd = [piece for piece in re.split(r'(\'.*?\'|".*?"| )', cur_script_name) if piece.strip()]
            script_cmd[0] = os.path.abspath(script_cmd[0])
            self.log(u'Absolute path to script: {0}'.format(script_cmd[0]), logger.DEBUG)

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
                self.log(u'Unable to run extra_script: {0!r}'.format(error))