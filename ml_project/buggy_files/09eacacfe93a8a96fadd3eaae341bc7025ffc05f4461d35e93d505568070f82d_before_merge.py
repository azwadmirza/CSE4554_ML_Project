        def _auto_concat_dataframe_chunks(chunk, inputs):
            if chunk.op.axis is not None:
                return pd.concat(inputs, axis=op.axis)

            # auto generated concat when executing a DataFrame
            if len(inputs) == 1:
                ret = inputs[0]
            else:
                max_rows = max(inp.index[0] for inp in chunk.inputs)
                min_rows = min(inp.index[0] for inp in chunk.inputs)
                n_rows = max_rows - min_rows + 1
                n_cols = int(len(inputs) // n_rows)
                assert n_rows * n_cols == len(inputs)

                xdf = pd if isinstance(inputs[0], (pd.DataFrame, pd.Series)) else cudf

                concats = []
                for i in range(n_rows):
                    if n_cols == 1:
                        concats.append(inputs[i])
                    else:
                        concat = xdf.concat([inputs[i * n_cols + j] for j in range(n_cols)], axis=1)
                        concats.append(concat)

                if xdf is pd:
                    # The `sort=False` is to suppress a `FutureWarning` of pandas,
                    # when the index or column of chunks to concatenate is not aligned,
                    # which may happens for certain ops.
                    #
                    # See also Note [Columns of Left Join] in test_merge_execution.py.
                    ret = xdf.concat(concats, sort=False)
                else:
                    ret = xdf.concat(concats)
                    # cuDF will lost index name when concat two seriess.
                    ret.index.name = concats[0].index.name

            if getattr(chunk.index_value, 'should_be_monotonic', False):
                ret.sort_index(inplace=True)
            if getattr(chunk.columns_value, 'should_be_monotonic', False):
                ret.sort_index(axis=1, inplace=True)
            return ret