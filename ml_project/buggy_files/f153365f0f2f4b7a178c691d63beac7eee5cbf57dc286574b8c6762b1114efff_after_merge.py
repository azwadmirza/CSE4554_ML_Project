    def _read_csv_from_file_pandas_on_ray(cls, filepath, kwargs={}):
        """Constructs a DataFrame from a CSV file.

        Args:
            filepath (str): path to the CSV file.
            npartitions (int): number of partitions for the DataFrame.
            kwargs (dict): args excluding filepath provided to read_csv.

        Returns:
            DataFrame or Series constructed from CSV file.
        """
        empty_pd_df = pandas.read_csv(filepath, **dict(kwargs, nrows=0, skipfooter=0))
        column_names = empty_pd_df.columns
        skipfooter = kwargs.get("skipfooter", None)
        skiprows = kwargs.pop("skiprows", None)
        parse_dates = kwargs.pop("parse_dates", False)
        partition_kwargs = dict(
            kwargs,
            header=None,
            names=column_names,
            skipfooter=0,
            skiprows=None,
            parse_dates=parse_dates,
        )
        with open(filepath, "rb") as f:
            # Get the BOM if necessary
            prefix = b""
            if kwargs.get("encoding", None) is not None:
                prefix = f.readline()
                partition_kwargs["skiprows"] = 1
                f.seek(0, os.SEEK_SET)  # Return to beginning of file

            prefix_id = ray.put(prefix)
            partition_kwargs_id = ray.put(partition_kwargs)
            # Skip the header since we already have the header information and skip the
            # rows we are told to skip.
            kwargs["skiprows"] = skiprows
            cls._skip_header(f, kwargs)
            # Launch tasks to read partitions
            partition_ids = []
            index_ids = []
            total_bytes = os.path.getsize(filepath)
            # Max number of partitions available
            num_parts = RayBlockPartitions._compute_num_partitions()
            # This is the number of splits for the columns
            num_splits = min(len(column_names), num_parts)
            # This is the chunksize each partition will read
            chunk_size = max(1, (total_bytes - f.tell()) // num_parts)

            while f.tell() < total_bytes:
                start = f.tell()
                f.seek(chunk_size, os.SEEK_CUR)
                f.readline()  # Read a whole number of lines
                partition_id = _read_csv_with_offset_pandas_on_ray._remote(
                    args=(
                        filepath,
                        num_splits,
                        start,
                        f.tell(),
                        partition_kwargs_id,
                        prefix_id,
                    ),
                    num_return_vals=num_splits + 1,
                )
                partition_ids.append(
                    [PandasOnRayRemotePartition(obj) for obj in partition_id[:-1]]
                )
                index_ids.append(partition_id[-1])

        index_col = kwargs.get("index_col", None)
        if index_col is None:
            new_index = pandas.RangeIndex(sum(ray.get(index_ids)))
        else:
            new_index_ids = get_index.remote([empty_pd_df.index.name], *index_ids)
            new_index = ray.get(new_index_ids)

        # If parse_dates is present, the column names that we have might not be
        # the same length as the returned column names. If we do need to modify
        # the column names, we remove the old names from the column names and
        # insert the new one at the front of the Index.
        if parse_dates is not None:
            # Check if is list of lists
            if isinstance(parse_dates, list) and isinstance(parse_dates[0], list):
                for group in parse_dates:
                    new_col_name = "_".join(group)
                    column_names = column_names.drop(group).insert(0, new_col_name)
            # Check if it is a dictionary
            elif isinstance(parse_dates, dict):
                for new_col_name, group in parse_dates.items():
                    column_names = column_names.drop(group).insert(0, new_col_name)

        new_query_compiler = PandasQueryCompiler(
            RayBlockPartitions(np.array(partition_ids)), new_index, column_names
        )

        if skipfooter:
            new_query_compiler = new_query_compiler.drop(
                new_query_compiler.index[-skipfooter:]
            )
        if kwargs.get("squeeze", False) and len(new_query_compiler.columns) == 1:
            return new_query_compiler[new_query_compiler.columns[0]]
        return new_query_compiler