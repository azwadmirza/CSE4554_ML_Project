def read_parquet(path, engine: str = "auto", columns=None,
                 groups_as_chunks=False, use_arrow_dtype=None,
                 incremental_index=False, storage_options=None,
                 **kwargs):
    """
    Load a parquet object from the file path, returning a DataFrame.

    Parameters
    ----------
    path : str, path object or file-like object
        Any valid string path is acceptable. The string could be a URL.
        For file URLs, a host is expected. A local file could be:
        ``file://localhost/path/to/table.parquet``.
        A file URL can also be a path to a directory that contains multiple
        partitioned parquet files. Both pyarrow and fastparquet support
        paths to directories as well as file URLs. A directory path could be:
        ``file://localhost/path/to/tables``.
        By file-like object, we refer to objects with a ``read()`` method,
        such as a file handler (e.g. via builtin ``open`` function)
        or ``StringIO``.
    engine : {'auto', 'pyarrow', 'fastparquet'}, default 'auto'
        Parquet library to use. The default behavior is to try 'pyarrow',
        falling back to 'fastparquet' if 'pyarrow' is unavailable.
    columns : list, default=None
        If not None, only these columns will be read from the file.
    groups_as_chunks : bool, default False
        if True, each row group correspond to a chunk.
        if False, each file correspond to a chunk.
        Only available for 'pyarrow' engine.
    incremental_index: bool, default False
        Create a new RangeIndex if csv doesn't contain index columns.
    use_arrow_dtype: bool, default None
        If True, use arrow dtype to store columns.
    storage_options: dict, optional
        Options for storage connection.
    **kwargs
        Any additional kwargs are passed to the engine.

    Returns
    -------
    Mars DataFrame
    """

    engine_type = check_engine(engine)
    engine = get_engine(engine_type)

    if os.path.isdir(path):
        # If path is a directory, we will read as a partitioned datasets.
        if engine_type != 'pyarrow':
            raise TypeError('Only support pyarrow engine when reading from'
                            'partitioned datasets.')
        dataset = pq.ParquetDataset(path)
        dtypes = dataset.schema.to_arrow_schema().empty_table().to_pandas().dtypes
        for partition in dataset.partitions:
            dtypes[partition.name] = pd.CategoricalDtype()
    else:
        if not isinstance(path, list):
            file_path = glob(path, storage_options=storage_options)[0]
        else:
            file_path = path[0]

        with open_file(file_path, storage_options=storage_options) as f:
            dtypes = engine.read_dtypes(f)

        if columns:
            dtypes = dtypes[columns]

        if use_arrow_dtype is None:
            use_arrow_dtype = options.dataframe.use_arrow_dtype
        if use_arrow_dtype:
            dtypes = to_arrow_dtypes(dtypes)

    index_value = parse_index(pd.RangeIndex(-1))
    columns_value = parse_index(dtypes.index, store_data=True)
    op = DataFrameReadParquet(path=path, engine=engine_type, columns=columns,
                              groups_as_chunks=groups_as_chunks,
                              use_arrow_dtype=use_arrow_dtype,
                              read_kwargs=kwargs,
                              incremental_index=incremental_index,
                              storage_options=storage_options)
    return op(index_value=index_value, columns_value=columns_value,
              dtypes=dtypes)