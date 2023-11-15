def sort_dataframe_result(df, result):
    """ sort DataFrame on client according to `should_be_monotonic` attribute """
    if hasattr(df, 'index_value'):
        if getattr(df.index_value, 'should_be_monotonic', False):
            result.sort_index(inplace=True)
        if hasattr(df, 'columns_value'):
            if getattr(df.columns_value, 'should_be_monotonic', False):
                result.sort_index(axis=1, inplace=True)
    return result