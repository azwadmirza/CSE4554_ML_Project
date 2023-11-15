    def _calc_chunk_params(cls, in_chunk, axes, chunk_shape, output, output_type,
                           chunk_op, no_shuffle: bool):
        params = {'index': in_chunk.index}
        if output_type == OutputType.tensor:
            shape_c = list(in_chunk.shape)
            for ax in axes:
                if not no_shuffle and chunk_shape[ax] > 1:
                    shape_c[ax] = np.nan
            params['shape'] = tuple(shape_c)
            params['dtype'] = in_chunk.dtype
            params['order'] = output.order
        elif output_type == OutputType.dataframe:
            shape_c = list(in_chunk.shape)
            if 0 in axes:
                if not no_shuffle and chunk_shape[0] > 1:
                    shape_c[0] = np.nan
            params['shape'] = tuple(shape_c)
            params['dtypes'] = output.dtypes
            params['columns_value'] = output.columns_value
            params['index_value'] = _shuffle_index_value(chunk_op, in_chunk.index_value)
        else:
            assert output_type == OutputType.series
            if no_shuffle:
                params['shape'] = in_chunk.shape
            else:
                params['shape'] = (np.nan,)
            params['name'] = in_chunk.name
            params['index_value'] = _shuffle_index_value(chunk_op, in_chunk.index_value)
            params['dtype'] = in_chunk.dtype
        return params