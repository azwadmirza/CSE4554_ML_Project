        def _auto_concat_series_chunks(chunk, inputs):
            # auto generated concat when executing a Series
            if all(np.isscalar(inp) for inp in inputs):
                return pd.Series(inputs)
            else:
                if len(inputs) == 1:
                    concat = inputs[0]
                else:
                    xdf = pd if isinstance(inputs[0], pd.Series) else cudf
                    if chunk.op.axis is not None:
                        concat = xdf.concat(inputs, axis=chunk.op.axis)
                    else:
                        concat = xdf.concat(inputs)
                if getattr(chunk.index_value, 'should_be_monotonic', False):
                    concat.sort_index(inplace=True)
                return concat