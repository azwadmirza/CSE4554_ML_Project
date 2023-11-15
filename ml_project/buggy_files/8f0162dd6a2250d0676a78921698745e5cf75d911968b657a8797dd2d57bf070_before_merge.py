def _fetch_csv_result(
    query_metadata: _QueryMetadata,
    keep_files: bool,
    chunksize: Optional[int],
    use_threads: bool,
    boto3_session: boto3.Session,
) -> Union[pd.DataFrame, Iterator[pd.DataFrame]]:
    _chunksize: Optional[int] = chunksize if isinstance(chunksize, int) else None
    _logger.debug("_chunksize: %s", _chunksize)
    if query_metadata.output_location is None or query_metadata.output_location.endswith(".csv") is False:
        chunked = _chunksize is not None
        return _empty_dataframe_response(chunked, query_metadata)
    path: str = query_metadata.output_location
    s3.wait_objects_exist(paths=[path], use_threads=False, boto3_session=boto3_session)
    _logger.debug("Start CSV reading from %s", path)
    ret = s3.read_csv(
        path=[path],
        dtype=query_metadata.dtype,
        parse_dates=query_metadata.parse_timestamps,
        converters=query_metadata.converters,
        quoting=csv.QUOTE_ALL,
        keep_default_na=False,
        na_values=[""],
        chunksize=_chunksize,
        skip_blank_lines=False,
        use_threads=False,
        boto3_session=boto3_session,
    )
    _logger.debug("Start type casting...")
    _logger.debug(type(ret))
    if _chunksize is None:
        df = _fix_csv_types(df=ret, parse_dates=query_metadata.parse_dates, binaries=query_metadata.binaries)
        df = _apply_query_metadata(df=df, query_metadata=query_metadata)
        if keep_files is False:
            s3.delete_objects(path=[path, f"{path}.metadata"], use_threads=use_threads, boto3_session=boto3_session)
        return df
    dfs = _fix_csv_types_generator(dfs=ret, parse_dates=query_metadata.parse_dates, binaries=query_metadata.binaries)
    dfs = _add_query_metadata_generator(dfs=dfs, query_metadata=query_metadata)
    if keep_files is False:
        return _delete_after_iterate(
            dfs=dfs, paths=[path, f"{path}.metadata"], use_threads=use_threads, boto3_session=boto3_session
        )
    return dfs