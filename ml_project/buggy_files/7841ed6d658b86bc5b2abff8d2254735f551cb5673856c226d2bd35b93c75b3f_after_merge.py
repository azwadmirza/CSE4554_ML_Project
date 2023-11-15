    def _sparse_reindex(cls, inp, index=None, columns=None):
        if inp.ndim == 2:
            columns = inp.columns if columns is None else columns
            index_shape = len(index) if index is not None else len(inp)
            i_to_columns = dict()

            for i, col in enumerate(columns):
                if col in inp.dtypes:
                    if index is None:
                        i_to_columns[i] = inp[col]
                    else:
                        indexer = inp.index.reindex(index)[1]
                        cond = indexer >= 0
                        available_indexer = indexer[cond]
                        del indexer
                        data = inp[col].iloc[available_indexer].to_numpy()
                        ind = cond.nonzero()[0]
                        spmatrix = sps.csc_matrix((data, (ind, np.zeros_like(ind))),
                                                  shape=(index_shape, 1), dtype=inp[col].dtype)
                        sparse_array = pd.arrays.SparseArray.from_spmatrix(spmatrix)
                        # convert to SparseDtype(xxx, np.nan)
                        # to ensure 0 in sparse_array not converted to np.nan
                        sparse_array = pd.arrays.SparseArray(
                            sparse_array.sp_values, sparse_index=sparse_array.sp_index,
                            fill_value=np.nan, dtype=pd.SparseDtype(sparse_array.dtype, np.nan))
                        series = pd.Series(sparse_array, index=index)

                        i_to_columns[i] = series
                else:
                    ind = index if index is not None else inp.index
                    i_to_columns[i] = pd.DataFrame.sparse.from_spmatrix(
                        sps.coo_matrix((index_shape, 1), dtype=np.float64),
                        index=ind).iloc[:, 0]

            df = pd.DataFrame(i_to_columns)
            df.columns = columns
            return df
        else:
            indexer = inp.index.reindex(index)[1]
            cond = indexer >= 0
            available_indexer = indexer[cond]
            del indexer
            data = inp.iloc[available_indexer].to_numpy()
            ind = cond.nonzero()[0]
            spmatrix = sps.csc_matrix((data, (ind, np.zeros_like(ind))),
                                      shape=(len(index), 1), dtype=inp.dtype)
            sparse_array = pd.arrays.SparseArray.from_spmatrix(spmatrix)
            # convert to SparseDtype(xxx, np.nan)
            # to ensure 0 in sparse_array not converted to np.nan
            sparse_array = pd.arrays.SparseArray(
                sparse_array.sp_values, sparse_index=sparse_array.sp_index,
                fill_value=np.nan, dtype=pd.SparseDtype(sparse_array.dtype, np.nan))
            series = pd.Series(sparse_array, index=index, name=inp.name)
            return series