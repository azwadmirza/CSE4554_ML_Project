    def from_file(cls, filename):
        filename = os.path.expanduser(filename)
        header, data = cls._parse_filepath(filename)
        return cls(data, header)