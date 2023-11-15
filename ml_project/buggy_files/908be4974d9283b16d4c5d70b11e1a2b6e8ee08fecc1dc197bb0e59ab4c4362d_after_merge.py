    def _get_data_from_filepath(self, filepath_or_buffer):
        """
        The function read_json accepts three input types:
            1. filepath (string-like)
            2. file-like object (e.g. open file object, StringIO)
            3. JSON string

        This method turns (1) into (2) to simplify the rest of the processing.
        It returns input types (2) and (3) unchanged.
        """
        data = filepath_or_buffer

        exists = False
        if isinstance(data, str):
            try:
                exists = os.path.exists(filepath_or_buffer)
            # gh-5874: if the filepath is too long will raise here
            except (TypeError, ValueError):
                pass

        if exists or self.compression is not None:
            data, _ = get_handle(
                filepath_or_buffer,
                "r",
                encoding=self.encoding,
                compression=self.compression,
            )
            self.should_close = True
            self.open_stream = data

        if isinstance(data, BytesIO):
            data = data.getvalue().decode()

        return data