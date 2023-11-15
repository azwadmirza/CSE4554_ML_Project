def to_numeric_df(kdf: 'ks.DataFrame') -> Tuple[pyspark.sql.DataFrame, List[str]]:
    """
    Takes a dataframe and turns it into a dataframe containing a single numerical
    vector of doubles. This dataframe has a single field called '_1'.

    TODO: index is not preserved currently
    :param kdf: the koalas dataframe.
    :return: a pair of dataframe, list of strings (the name of the columns
             that were converted to numerical types)

    >>> to_numeric_df(ks.DataFrame({'A': [0, 1], 'B': [1, 0], 'C': ['x', 'y']}))
    (DataFrame[_correlation_output: vector], ['A', 'B'])
    """
    # TODO, it should be more robust.
    accepted_types = {np.dtype(dt) for dt in [np.int8, np.int16, np.int32, np.int64,
                                              np.float32, np.float64, np.bool_]}
    numeric_fields = [fname for fname in kdf._internal.data_columns
                      if kdf[fname].dtype in accepted_types]
    numeric_df = kdf._sdf.select(*numeric_fields)
    va = VectorAssembler(inputCols=numeric_fields, outputCol=CORRELATION_OUTPUT_COLUMN)
    v = va.transform(numeric_df).select(CORRELATION_OUTPUT_COLUMN)
    return v, numeric_fields