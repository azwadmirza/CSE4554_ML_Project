    def _read_parquet_path(session_primitives: "SessionPrimitives",
                           path: str,
                           columns: Optional[List[str]] = None,
                           filters: Optional[Union[List[Tuple[Any]], List[List[Tuple[Any]]]]] = None,
                           procs_cpu_bound: Optional[int] = None,
                           wait_objects: bool = False,
                           wait_objects_timeout: Optional[float] = 10.0) -> pd.DataFrame:
        """
        Read parquet data from S3

        :param session_primitives: SessionPrimitives()
        :param path: AWS S3 path (E.g. s3://bucket-name/folder_name/)
        :param columns: Names of columns to read from the file
        :param filters: List of filters to apply, like ``[[('x', '=', 0), ...], ...]``.
        :param procs_cpu_bound: Number of cores used for CPU bound tasks
        :param wait_objects: Wait for all files exists (Not valid when path is a directory) (Useful for eventual consistency situations)
        :param wait_objects: Wait objects Timeout (seconds)
        :return: Pandas DataFrame
        """
        session: Session = session_primitives.session
        if wait_objects is True:
            logger.debug(f"waiting {path}...")
            session.s3.wait_object_exists(path=path, timeout=wait_objects_timeout)
            is_file: bool = True
        else:
            logger.debug(f"checking if {path} exists...")
            is_file = session.s3.does_object_exists(path=path)
            if is_file is False:
                path = path[:-1] if path[-1] == "/" else path
        logger.debug(f"is_file: {is_file}")
        procs_cpu_bound = procs_cpu_bound if procs_cpu_bound is not None else session_primitives.procs_cpu_bound if session_primitives.procs_cpu_bound is not None else 1
        use_threads: bool = True if procs_cpu_bound > 1 else False
        logger.debug(f"Reading Parquet: {path}")
        if is_file is True:
            client_s3 = session.boto3_session.client(service_name="s3", use_ssl=True, config=session.botocore_config)
            bucket, key = path.replace("s3://", "").split("/", 1)
            obj = client_s3.get_object(Bucket=bucket, Key=key)
            table = pq.ParquetFile(source=BytesIO(obj["Body"].read())).read(columns=columns, use_threads=use_threads)
        else:
            fs: S3FileSystem = get_fs(session_primitives=session_primitives)
            fs = pa.filesystem._ensure_filesystem(fs)
            fs.invalidate_cache()
            table = pq.read_table(source=path, columns=columns, filters=filters, filesystem=fs, use_threads=use_threads)
        # Check if we lose some integer during the conversion (Happens when has some null value)
        integers = [field.name for field in table.schema if str(field.type).startswith("int") and field.name != "__index_level_0__"]
        logger.debug(f"Converting to Pandas: {path}")
        df = table.to_pandas(use_threads=use_threads, integer_object_nulls=True)
        logger.debug(f"Casting Int64 columns: {path}")
        for c in integers:
            if not str(df[c].dtype).startswith("int"):
                df[c] = df[c].astype("Int64")
        logger.debug(f"Done: {path}")
        return df