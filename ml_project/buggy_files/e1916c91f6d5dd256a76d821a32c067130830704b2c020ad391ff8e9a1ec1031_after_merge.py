    def run(self):
        """ Get the downloaded and/or snatched history """
        history = History().get(self.limit, self.type).detailed

        def make_result(cur_item, cur_type):
            """
            Make an API result from a history item

            :param cur_item: to convert to API item
            :param cur_type: the type of action to return

            :returns: an API result
            """

            def convert_date(history_date):
                """
                Convert date from a history date to datetime format
                :param history_date: a date from the history
                :return: a formatted date string
                """
                return datetime.strptime(
                    text_type(history_date),
                    History.date_format
                ).strftime(dateTimeFormat)

            if cur_type in (statusStrings[cur_item.action].lower(), None):
                return {
                    'date': convert_date(cur_item.date),
                    'episode': cur_item.episode,
                    'indexer': cur_item.indexer,
                    'provider': cur_item.provider,
                    'quality': get_quality_string(cur_item.quality),
                    'resource': os.path.basename(cur_item.resource),
                    'resource_path': os.path.dirname(cur_item.resource),
                    'season': cur_item.season,
                    'show_name': cur_item.show_name,
                    'status': statusStrings[cur_item.action],
                    # Add tvdbid for backward compatibility
                    # TODO: Make this actual tvdb id for other indexers
                    'tvdbid': cur_item.series_id,
                }

        results = [make_result(x, self.type) for x in history if x]
        return _responds(RESULT_SUCCESS, results)