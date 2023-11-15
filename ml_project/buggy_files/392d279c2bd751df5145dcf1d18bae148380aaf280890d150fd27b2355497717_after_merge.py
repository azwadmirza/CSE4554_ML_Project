def dataframe_getitem(df, item):
    columns = df.columns_value.to_pandas()
    if isinstance(item, list):
        for col_name in item:
            if col_name not in columns:
                raise KeyError('%s not in columns' % col_name)
        op = DataFrameIndex(col_names=item, object_type=ObjectType.dataframe)
    elif isinstance(item, SERIES_TYPE) and item.dtype == np.bool:
        op = DataFrameIndex(mask=item, object_type=ObjectType.dataframe)
    elif isinstance(item, pd.Series) and item.dtype == np.bool:
        op = DataFrameIndex(mask=item, object_type=ObjectType.dataframe)
    else:
        if item not in columns:
            raise KeyError('%s not in columns' % item)
        op = DataFrameIndex(col_names=item)
    return op(df)