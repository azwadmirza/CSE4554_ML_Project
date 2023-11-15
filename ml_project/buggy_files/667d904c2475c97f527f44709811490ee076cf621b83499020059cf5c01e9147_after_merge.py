    def add_file(self, filepath, delimiter=','):
        """Add a CSV, JSONL or a PLASO file to the buffer.

        Args:
            filepath: the path to the file to add.
            delimiter: if this is a CSV file then a delimiter can be defined.

        Raises:
            TypeError: if the entry does not fulfill requirements.
        """
        self._ready()

        if not os.path.isfile(filepath):
            raise TypeError('Entry object needs to be a file that exists.')

        file_ending = filepath.lower().split('.')[-1]
        if file_ending == 'csv':
            data_frame = pandas.read_csv(filepath, delimiter=delimiter)
            self.add_data_frame(data_frame)
        elif file_ending == 'plaso':
            self._sketch.upload(self._timeline_name, filepath)
        elif file_ending == 'jsonl':
            data_frame = None
            with open(filepath, 'r') as fh:
                lines = [json.loads(x) for x in fh]
                data_frame = pandas.DataFrame(lines)
            if data_frame is None:
                raise TypeError('Unable to parse the JSON file.')
            if data_frame.empty:
                raise TypeError('Is the JSON file empty?')

            self.add_data_frame(data_frame)
        else:
            raise TypeError(
                'File needs to have a file extension of: .csv, .jsonl or '
                '.plaso')