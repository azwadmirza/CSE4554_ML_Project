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