    def process_input(
        cls,
        query: Union[LocalPath, lavalink.Track, "Query", str],
        _local_folder_current_path: Path,
        **kwargs,
    ) -> "Query":
        """
        Process the input query into its type

        Parameters
        ----------
        query : Union[Query, LocalPath, lavalink.Track, str]
            The query string or LocalPath object.
        _local_folder_current_path: Path
            The Current Local Track folder
        Returns
        -------
        Query
            Returns a parsed Query object.
        """
        if not query:
            query = "InvalidQueryPlaceHolderName"
        possible_values = {}

        if isinstance(query, str):
            query = query.strip("<>")
            while "ytsearch:" in query:
                query = query.replace("ytsearch:", "")
            while "scsearch:" in query:
                query = query.replace("scsearch:", "")

        elif isinstance(query, Query):
            for key, val in kwargs.items():
                setattr(query, key, val)
            return query
        elif isinstance(query, lavalink.Track):
            possible_values["stream"] = query.is_stream
            query = query.uri

        possible_values.update(dict(**kwargs))
        possible_values.update(cls._parse(query, _local_folder_current_path, **kwargs))
        return cls(query, _local_folder_current_path, **possible_values)