    def parse(fname, **kwargs):
        num_splits = kwargs.pop("num_splits", None)
        columns = kwargs.get("columns", None)
        if fname.startswith("s3://"):
            from botocore.exceptions import NoCredentialsError
            import s3fs

            try:
                fs = s3fs.S3FileSystem()
                fname = fs.open(fname)
            except NoCredentialsError:
                fs = s3fs.S3FileSystem(anon=True)
                fname = fs.open(fname)

        if num_splits is None:
            return pandas.read_parquet(fname, **kwargs)
        kwargs["use_pandas_metadata"] = True
        df = pandas.read_parquet(fname, **kwargs)
        if isinstance(df.index, pandas.RangeIndex):
            idx = len(df.index)
        else:
            idx = df.index
        columns = [c for c in columns if c not in df.index.names and c in df.columns]
        if columns is not None:
            df = df[columns]
        # Append the length of the index here to build it externally
        return _split_result_for_readers(0, num_splits, df) + [idx, df.dtypes]