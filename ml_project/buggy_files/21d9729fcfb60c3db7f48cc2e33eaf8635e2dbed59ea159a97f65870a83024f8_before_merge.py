    def _atime_expr(self):
        """If max_items is set, return an expression to limit the query."""
        max_items = config.get('completion', 'web-history-max-items')
        # HistoryCategory should not be added to the completion in that case.
        assert max_items != 0

        if max_items < 0:
            return ''

        min_atime = sql.Query(' '.join([
            'SELECT min(last_atime) FROM',
            '(SELECT last_atime FROM CompletionHistory',
            'ORDER BY last_atime DESC LIMIT :limit)',
        ])).run(limit=max_items).value()

        return "AND last_atime >= {}".format(min_atime)