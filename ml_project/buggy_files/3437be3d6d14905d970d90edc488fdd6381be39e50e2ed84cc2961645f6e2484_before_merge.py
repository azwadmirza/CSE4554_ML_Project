    def _parse_csv(filepath):
        """Parses an GOES CSV"""
        with open(filepath, 'rb') as fp:
            # @todo: check for:
            # "No-Data-Found for the time period requested..." error
            return "", read_csv(fp, sep=",", index_col=0, parse_dates=True)