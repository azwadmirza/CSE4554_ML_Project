    def __setstate__(self, state):
        fetch_op_type, fetch_op_id, output_types, params, nsplits, chunk_infos = state
        params['nsplits'] = nsplits
        chunks = []
        for ci in chunk_infos:
            chunk_op_type, chunk_op_output_types, chunk_key, chunk_id, chunk_params = ci
            chunk = chunk_op_type(output_types=chunk_op_output_types).new_chunk(
                None, _key=chunk_key, _id=chunk_id, kws=[chunk_params])
            chunks.append(chunk)
        params['chunks'] = chunks
        self.tileable = fetch_op_type(
            _id=fetch_op_id, output_types=output_types).new_tileable(None, kws=[params])