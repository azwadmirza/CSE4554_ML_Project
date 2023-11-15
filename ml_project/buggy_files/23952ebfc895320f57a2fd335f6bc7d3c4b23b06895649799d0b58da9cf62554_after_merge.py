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