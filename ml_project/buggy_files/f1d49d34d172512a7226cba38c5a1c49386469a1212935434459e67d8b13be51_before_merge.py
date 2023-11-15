    def _get_events_which_are_prevs(self, event_ids):
        """Filter the supplied list of event_ids to get those which are prev_events of
        existing (non-outlier/rejected) events.

        Args:
            event_ids (Iterable[str]): event ids to filter

        Returns:
            Deferred[List[str]]: filtered event ids
        """
        results = []

        def _get_events(txn, batch):
            sql = """
            SELECT prev_event_id
            FROM event_edges
                INNER JOIN events USING (event_id)
                LEFT JOIN rejections USING (event_id)
            WHERE
                prev_event_id IN (%s)
                AND NOT events.outlier
                AND rejections.event_id IS NULL
            """ % (
                ",".join("?" for _ in batch),
            )

            txn.execute(sql, batch)
            results.extend(r[0] for r in txn)

        for chunk in batch_iter(event_ids, 100):
            yield self.runInteraction("_get_events_which_are_prevs", _get_events, chunk)

        defer.returnValue(results)