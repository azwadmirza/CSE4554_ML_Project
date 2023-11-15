    def from_file(cls, filename):
        filename = os.path.expanduser(filename)
        header, data = cls._parse_filepath(filename)
        if data.empty == True:
            raise ValueError("No data found!")
        else:               
            return cls(data, header)