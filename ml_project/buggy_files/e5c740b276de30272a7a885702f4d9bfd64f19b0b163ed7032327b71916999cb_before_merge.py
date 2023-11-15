def calc_columns_index(column_name, df):
    """
    Calculate the chunk index on the axis 1 according to the selected column.
    :param column_name: selected column name
    :param df: input tiled DataFrame
    :return: chunk index on the columns axis
    """
    column_nsplits = df.nsplits[1]
    column_loc = df.columns.to_pandas().get_loc(column_name)
    return np.searchsorted(np.cumsum(column_nsplits), column_loc + 1)