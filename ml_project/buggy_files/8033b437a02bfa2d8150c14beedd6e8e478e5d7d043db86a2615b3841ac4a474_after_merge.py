def fetch_table_data(
    table_cache, path, cache="disk", cats_only=False, reader=None, columns=None, **kwargs
):
    """Utility to retrieve a cudf DataFrame from a cache (and add the
    DataFrame to a cache if the element is missing).  Note that `cats_only=True`
    results in optimized logic for the `Categorify` transformation.
    """
    table = table_cache.get(path, None)
    if table and not isinstance(table, cudf.DataFrame):
        if not cats_only:
            return cudf.io.read_parquet(table, index=False)
        df = cudf.io.read_parquet(table, index=False, columns=columns)
        df.index.name = "labels"
        df.reset_index(drop=False, inplace=True)
        return df

    reader = reader or cudf.io.read_parquet
    if table is None:
        if cache in ("device", "disk"):
            table = reader(path, index=False, columns=columns, **kwargs)
        elif cache == "host":
            if reader == cudf.io.read_parquet:
                # If the file is already in parquet format,
                # we can just move the same bytes to host memory
                with fsspec.open(path, "rb") as f:
                    table_cache[path] = BytesIO(f.read())
                table = reader(table_cache[path], index=False, columns=columns, **kwargs)
            else:
                # Otherwise, we should convert the format to parquet
                table = reader(path, index=False, columns=columns, **kwargs)
                table_cache[path] = BytesIO()
                table.to_parquet(table_cache[path])
        if cats_only:
            table.index.name = "labels"
            table.reset_index(drop=False, inplace=True)
        if cache == "device":
            table_cache[path] = table.copy(deep=False)
    return table