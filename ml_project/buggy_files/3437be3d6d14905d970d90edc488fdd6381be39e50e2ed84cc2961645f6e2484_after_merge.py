    def _parse_csv(filepath):
        """Parses an GOES CSV"""
        with open(filepath, 'rb') as fp:
            return "", read_csv(fp, sep=",", index_col=0, parse_dates=True)