def combine_tickers_with_mean(tickers: Dict[str, pd.DataFrame], column: str = "close"):
    """
    Combine multiple dataframes "column"
    :param tickers: Dict of Dataframes, dict key should be pair.
    :param column: Column in the original dataframes to use
    :return: DataFrame with the column renamed to the dict key, and a column
        named mean, containing the mean of all pairs.
    """
    df_comb = pd.concat([tickers[pair].set_index('date').rename(
        {column: pair}, axis=1)[pair] for pair in tickers], axis=1)

    df_comb['mean'] = df_comb.mean(axis=1)

    return df_comb