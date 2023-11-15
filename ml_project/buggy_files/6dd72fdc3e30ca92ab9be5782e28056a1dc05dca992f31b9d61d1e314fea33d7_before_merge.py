    def __setstate__(self, state):
        fetch_op_type, fetch_op_id, params, nsplits, chunk_infos = state
        params['nsplits'] = nsplits
        chunks = []
        for ci in chunk_infos:
            chunk = ci[0]().new_chunk(None, _key=ci[1], _id=ci[2], kws=[ci[3]])
            chunks.append(chunk)
        params['chunks'] = chunks
        self.tileable = fetch_op_type(_id=fetch_op_id).new_tileable(None, kws=[params])