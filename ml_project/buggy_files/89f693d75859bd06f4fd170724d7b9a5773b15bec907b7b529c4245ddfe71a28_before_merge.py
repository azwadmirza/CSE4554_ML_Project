    def conv_csv_shadowserver(self, value):
        """
        Converts a dict to shadowservers csv quoting format.

        Numeric: no quoting
        Empty string: no quoting
        Else: " quoting
        """
        try:
            if str(int(value)) == value:
                return str(value)
        except ValueError:
            if hasattr(value, '__len__') and not len(value):
                return ''
            else:
                return '"' + value + '"'