    def execute(cls, ctx, op):
        def _base_concat(chunk, inputs):
            # auto generated concat when executing a DataFrame, Series or Index
            if chunk.op.output_types[0] == OutputType.dataframe:
                return _auto_concat_dataframe_chunks(chunk, inputs)
            elif chunk.op.output_types[0] == OutputType.series:
                return _auto_concat_series_chunks(chunk, inputs)
            elif chunk.op.output_types[0] == OutputType.index:
                return _auto_concat_index_chunks(chunk, inputs)
            elif chunk.op.output_types[0] == OutputType.categorical:
                return _auto_concat_categorical_chunks(chunk, inputs)
            else:  # pragma: no cover
                raise TypeError('Only DataFrameChunk, SeriesChunk, IndexChunk, '
                                'and CategoricalChunk can be automatically concatenated')

        def _auto_concat_dataframe_chunks(chunk, inputs):
            xdf = pd if isinstance(inputs[0], (pd.DataFrame, pd.Series)) or cudf is None else cudf

            if chunk.op.axis is not None:
                return xdf.concat(inputs, axis=op.axis)

            # auto generated concat when executing a DataFrame
            if len(inputs) == 1:
                ret = inputs[0]
            else:
                n_rows = len(set(inp.index[0] for inp in chunk.inputs))
                n_cols = int(len(inputs) // n_rows)
                assert n_rows * n_cols == len(inputs)

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

        def _auto_concat_series_chunks(chunk, inputs):
            # auto generated concat when executing a Series
            if len(inputs) == 1:
                concat = inputs[0]
            else:
                xdf = pd if isinstance(inputs[0], pd.Series) or cudf is None else cudf
                if chunk.op.axis is not None:
                    concat = xdf.concat(inputs, axis=chunk.op.axis)
                else:
                    concat = xdf.concat(inputs)
            if getattr(chunk.index_value, 'should_be_monotonic', False):
                concat.sort_index(inplace=True)
            return concat

        def _auto_concat_index_chunks(chunk, inputs):
            if len(inputs) == 1:
                xdf = pd if isinstance(inputs[0], pd.Index) or cudf is None else cudf
                concat_df = xdf.DataFrame(index=inputs[0])
            else:
                xdf = pd if isinstance(inputs[0], pd.Index) or cudf is None else cudf
                empty_dfs = [xdf.DataFrame(index=inp) for inp in inputs]
                concat_df = xdf.concat(empty_dfs, axis=0)
            if getattr(chunk.index_value, 'should_be_monotonic', False):
                concat_df.sort_index(inplace=True)
            return concat_df.index

        def _auto_concat_categorical_chunks(_, inputs):
            if len(inputs) == 1:  # pragma: no cover
                return inputs[0]
            else:
                # convert categorical into array
                arrays = [np.asarray(inp) for inp in inputs]
                array = np.concatenate(arrays)
                return pd.Categorical(array, categories=inputs[0].categories,
                                      ordered=inputs[0].ordered)

        chunk = op.outputs[0]
        inputs = [ctx[input.key] for input in op.inputs]

        if isinstance(inputs[0], tuple):
            ctx[chunk.key] = tuple(_base_concat(chunk, [input[i] for input in inputs])
                                   for i in range(len(inputs[0])))
        else:
            ctx[chunk.key] = _base_concat(chunk, inputs)