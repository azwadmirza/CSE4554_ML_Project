    def _calc_bool_index_param(cls,
                               input_index_value: IndexValue,
                               pd_index: pd.Index,
                               inp,
                               index,
                               axis: int) -> Dict:
        param = dict()
        if input_index_value.has_value():
            if isinstance(index, np.ndarray):
                filtered_index = pd_index[index]
                param['shape'] = len(filtered_index)
                param['index_value'] = parse_index(filtered_index,
                                                   store_data=axis == 1)
                if axis == 1:
                    param['dtypes'] = inp.dtypes[index]
            else:
                # tensor, cannot be indexer on axis 1
                assert axis == 0
                param['shape'] = np.nan
                param['index_value'] = parse_index(pd.Index([], dtype=pd_index.dtype),
                                                   inp, index, store_data=False)
        else:
            assert axis == 0
            if isinstance(index, np.ndarray):
                param['shape'] = int(index.sum())
            else:
                param['shape'] = np.nan
            param['index_value'] = parse_index(pd_index, inp, index,
                                               store_data=False)

        return param