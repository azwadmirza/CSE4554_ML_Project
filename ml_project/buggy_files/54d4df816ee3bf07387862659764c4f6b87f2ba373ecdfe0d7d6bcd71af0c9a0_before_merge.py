    def _finalize(self, parse_result):
        """
        Store parse result if it is complete and final

        :param parse_result: Result of parsers
        """
        self.release_group = parse_result.release_group

        # remember whether it's a proper
        if parse_result.extra_info:
            self.is_proper = re.search(r'(^|[\. _-])(proper|repack)([\. _-]|$)', parse_result.extra_info, re.I) is not None

        # if the result is complete then remember that for later
        # if the result is complete then set release name
        if parse_result.series_name and ((parse_result.season_number is not None and parse_result.episode_numbers) or
                                         parse_result.air_date) and parse_result.release_group:

            if not self.release_name:
                self.release_name = helpers.remove_non_release_groups(remove_extension(ek(os.path.basename, parse_result.original_name)))

        else:
            logger.log(u"Parse result not sufficient (all following have to be set). will not save release name",
                       logger.DEBUG)
            logger.log(u"Parse result(series_name): " + str(parse_result.series_name), logger.DEBUG)
            logger.log(u"Parse result(season_number): " + str(parse_result.season_number), logger.DEBUG)
            logger.log(u"Parse result(episode_numbers): " + str(parse_result.episode_numbers), logger.DEBUG)
            logger.log(u" or Parse result(air_date): " + str(parse_result.air_date), logger.DEBUG)
            logger.log(u"Parse result(release_group): " + str(parse_result.release_group), logger.DEBUG)