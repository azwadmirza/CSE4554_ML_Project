def copy_df_for_func(func):
    """
    Create a function that copies the dataframe, likely because `func` is inplace.

    Parameters
    ----------
    func : callable
        The function, usually updates a dataframe inplace.

    Returns
    -------
    callable
        A callable function to be applied in the partitions
    """

    def caller(df, *args, **kwargs):
        df = df.copy()
        func(df, *args, **kwargs)
        return df

    return caller