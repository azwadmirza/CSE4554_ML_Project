    def concat_tileable_chunks(cls, tileable):
        from .merge.concat import DataFrameConcat, GroupByConcat
        from .operands import ObjectType, DATAFRAME_TYPE, SERIES_TYPE, GROUPBY_TYPE

        df = tileable
        assert not df.is_coarse()

        if isinstance(df, DATAFRAME_TYPE):
            chunk = DataFrameConcat(object_type=ObjectType.dataframe).new_chunk(
                df.chunks, shape=df.shape, index=(0, 0), dtypes=df.dtypes,
                index_value=df.index_value, columns_value=df.columns_value)
            return DataFrameConcat(object_type=ObjectType.dataframe).new_dataframe(
                [df], shape=df.shape, chunks=[chunk],
                nsplits=tuple((s,) for s in df.shape), dtypes=df.dtypes,
                index_value=df.index_value, columns_value=df.columns_value)
        elif isinstance(df, SERIES_TYPE):
            chunk = DataFrameConcat(object_type=ObjectType.series).new_chunk(
                df.chunks, shape=df.shape, index=(0,), dtype=df.dtype,
                index_value=df.index_value, name=df.name)
            return DataFrameConcat(object_type=ObjectType.series).new_series(
                [df], shape=df.shape, chunks=[chunk],
                nsplits=tuple((s,) for s in df.shape), dtype=df.dtype,
                index_value=df.index_value, name=df.name)
        elif isinstance(df, GROUPBY_TYPE):
            chunk = GroupByConcat(by=df.op.by, object_type=ObjectType.dataframe).new_chunk(df.chunks)
            return GroupByConcat(by=df.op.by, object_type=ObjectType.dataframe).new_dataframe([df], chunks=[chunk])
        else:
            raise NotImplementedError