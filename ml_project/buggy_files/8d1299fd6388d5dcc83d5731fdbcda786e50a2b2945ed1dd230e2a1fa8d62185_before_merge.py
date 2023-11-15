    def _calc_dataframe_params(cls, chunk_index_to_chunks, chunk_shape):
        dtypes = pd.concat([chunk_index_to_chunks[0, i].dtypes
                            for i in range(chunk_shape[1])])
        columns_value = parse_index(dtypes.index, store_data=True)
        pd_indxes = [chunk_index_to_chunks[i, 0].index_value.to_pandas()
                     for i in range(chunk_shape[0])]
        pd_index = reduce(lambda x, y: x.append(y), pd_indxes)
        index_value = parse_index(pd_index)
        return {'dtypes': dtypes, 'columns_value': columns_value,
                'index_value': index_value}