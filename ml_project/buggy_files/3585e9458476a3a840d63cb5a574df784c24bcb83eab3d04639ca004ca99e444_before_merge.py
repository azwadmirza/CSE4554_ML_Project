    def fetch_chunks_data(self, session_id, chunk_indexes, chunk_keys, nsplits,
                          index_obj=None, serial=True, serial_type=None,
                          compressions=None, pickle_protocol=None):
        chunk_index_to_key = dict((index, key) for index, key in zip(chunk_indexes, chunk_keys))
        if not index_obj:
            chunk_results = dict((idx, self.fetch_chunk_data(session_id, k)) for
                                 idx, k in zip(chunk_indexes, chunk_keys))
        else:
            chunk_results = dict()
            indexes = dict()
            for axis, s in enumerate(index_obj):
                idx_to_slices = slice_split(s, nsplits[axis])
                indexes[axis] = idx_to_slices
            for chunk_index in itertools.product(*[v.keys() for v in indexes.values()]):
                # slice_obj: use tuple, since numpy complains
                #
                # FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated; use
                # `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array
                # index, `arr[np.array(seq)]`, which will result either in an error or a different result.
                slice_obj = tuple(indexes[axis][chunk_idx] for axis, chunk_idx in enumerate(chunk_index))
                chunk_key = chunk_index_to_key[chunk_index]
                chunk_results[chunk_index] = self.fetch_chunk_data(session_id, chunk_key, slice_obj)

        chunk_results = [(idx, dataserializer.loads(f.result())) for
                         idx, f in chunk_results.items()]
        if len(chunk_results) == 1:
            ret = chunk_results[0][1]
        else:
            ret = merge_chunks(chunk_results)
        if not serial:
            return ret
        compressions = max(compressions) if compressions else dataserializer.CompressType.NONE
        return dataserializer.dumps(ret, serial_type=serial_type, compress=compressions,
                                    pickle_protocol=pickle_protocol)