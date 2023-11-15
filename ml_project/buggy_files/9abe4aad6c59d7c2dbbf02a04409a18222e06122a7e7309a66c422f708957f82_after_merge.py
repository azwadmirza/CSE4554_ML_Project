    def set_pattern(self, pattern):
        """Set the pattern used to filter results.

        Args:
            pattern: string pattern to filter by.
        """
        # escape to treat a user input % or _ as a literal, not a wildcard
        pattern = pattern.replace('%', '\\%')
        pattern = pattern.replace('_', '\\_')
        words = ['%{}%'.format(w) for w in pattern.split(' ')]

        # build a where clause to match all of the words in any order
        # given the search term "a b", the WHERE clause would be:
        # ((url || ' ' || title) LIKE '%a%') AND
        # ((url || ' ' || title) LIKE '%b%')
        where_clause = ' AND '.join(
            "(url || ' ' || title) LIKE :{} escape '\\'".format(i)
            for i in range(len(words)))

        # replace ' in timestamp-format to avoid breaking the query
        timestamp_format = config.val.completion.timestamp_format or ''
        timefmt = ("strftime('{}', last_atime, 'unixepoch', 'localtime')"
                   .format(timestamp_format.replace("'", "`")))

        try:
            if (not self._query or
                    len(words) != len(self._query.bound_values())):
                # if the number of words changed, we need to generate a new
                # query otherwise, we can reuse the prepared query for
                # performance
                self._query = sql.Query(' '.join([
                    "SELECT url, title, {}".format(timefmt),
                    "FROM CompletionHistory",
                    # the incoming pattern will have literal % and _ escaped we
                    # need to tell sql to treat '\' as an escape character
                    'WHERE ({})'.format(where_clause),
                    self._atime_expr(),
                    "ORDER BY last_atime DESC",
                ]), forward_only=False)

            with debug.log_time('sql', 'Running completion query'):
                self._query.run(**{
                    str(i): w for i, w in enumerate(words)})
        except sql.SqlKnownError as e:
            # Sometimes, the query we built up was invalid, for example,
            # due to a large amount of words.
            message.error("Error with SQL Query: {}".format(e.text()))
            return
        self.setQuery(self._query.query)