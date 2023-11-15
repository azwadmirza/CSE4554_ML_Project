    def __getstate__(self):
        fetch_op = self.tileable.op
        fetch_tileable = self.tileable
        chunk_infos = [(type(c.op), c.key, c.id, c.params) for c in fetch_tileable.chunks]
        return type(fetch_op), fetch_op.id, fetch_tileable.params, \
            fetch_tileable.nsplits, chunk_infos