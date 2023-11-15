    def from_csv(cls, path, sep=',', parse_dates=True):
        """
        Read delimited file into Series

        Parameters
        ----------
        path : string
        sep : string, default ','
            Field delimiter
        parse_dates : boolean, default True
            Parse dates. Different default from read_table

        Returns
        -------
        y : Series
        """
        from pandas.core.frame import DataFrame
        df = DataFrame.from_csv(path, header=None, sep=sep, parse_dates=parse_dates)
        return df[df.columns[0]]