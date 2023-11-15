    def _calc_chunk_params(cls, in_chunk, axes, output, output_type, chunk_op):
        params = {'index': in_chunk.index}
        if output_type == OutputType.tensor:
            chunk_shape = list(in_chunk.shape)
            for ax in axes:
                chunk_shape[ax] = np.nan
            params['shape'] = tuple(chunk_shape)
            params['dtype'] = in_chunk.dtype
            params['order'] = output.order
        elif output_type == OutputType.dataframe:
            chunk_shape = list(in_chunk.shape)
            if 0 in axes:
                chunk_shape[0] = np.nan
            params['shape'] = tuple(chunk_shape)
            params['dtypes'] = output.dtypes
            params['columns_value'] = output.columns_value
            params['index_value'] = _shuffle_index_value(chunk_op, in_chunk.index_value)
        else:
            assert output_type == OutputType.series
            params['shape'] = (np.nan,)
            params['name'] = in_chunk.name
            params['index_value'] = _shuffle_index_value(chunk_op, in_chunk.index_value)
            params['dtype'] = in_chunk.dtype
        return params