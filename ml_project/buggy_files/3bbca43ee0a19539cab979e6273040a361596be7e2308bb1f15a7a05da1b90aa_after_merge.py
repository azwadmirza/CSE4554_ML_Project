    def tile(cls, op: 'DataFrameRename'):
        inp = op.inputs[0]
        out = op.outputs[0]
        chunks = []

        dtypes_cache = dict()
        for c in inp.chunks:
            params = c.params
            new_op = op.copy().reset_key()

            if op.columns_mapper is not None:
                try:
                    new_dtypes = dtypes_cache[c.index[0]]
                except KeyError:
                    new_dtypes = dtypes_cache[c.index[0]] = op._calc_renamed_df(c).dtypes

                params['columns_value'] = parse_index(new_dtypes.index, store_data=True)
                params['dtypes'] = new_dtypes
            if op.index_mapper is not None:
                params['index_value'] = out.index_value
            if op.new_name is not None:
                params['name'] = out.name

            if isinstance(op.columns_mapper, dict):
                idx = params['dtypes'].index
                if op._level is not None:
                    idx = idx.get_level_values(op._level)
                new_op._columns_mapper = {k: v for k, v in op.columns_mapper.items()
                                          if v in idx}
            chunks.append(new_op.new_chunk([c], **params))

        new_op = op.copy().reset_key()
        return new_op.new_tileables([inp], chunks=chunks, nsplits=inp.nsplits, **out.params)