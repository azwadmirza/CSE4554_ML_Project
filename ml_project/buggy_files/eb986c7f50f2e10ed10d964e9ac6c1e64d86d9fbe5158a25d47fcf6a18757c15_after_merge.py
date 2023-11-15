    def get_column_names(self, virtual=True, strings=True, hidden=False, regex=None, alias=True):
        """Return a list of column names

        Example:

        >>> import vaex
        >>> df = vaex.from_scalars(x=1, x2=2, y=3, s='string')
        >>> df['r'] = (df.x**2 + df.y**2)**2
        >>> df.get_column_names()
        ['x', 'x2', 'y', 's', 'r']
        >>> df.get_column_names(virtual=False)
        ['x', 'x2', 'y', 's']
        >>> df.get_column_names(regex='x.*')
        ['x', 'x2']

        :param virtual: If False, skip virtual columns
        :param hidden: If False, skip hidden columns
        :param strings: If False, skip string columns
        :param regex: Only return column names matching the (optional) regular expression
        :param alias: Return the alias (True) or internal name (False).
        :rtype: list of str
        """
        aliases_reverse = {value: key for key, value in self._column_aliases.items()} if alias else {}
        def column_filter(name):
            '''Return True if column with specified name should be returned'''
            if regex and not re.match(regex, name):
                return False
            if not virtual and name in self.virtual_columns:
                return False
            if not strings and (self.dtype(name) == str_type or self.dtype(name).type == np.string_):
                return False
            if not hidden and name.startswith('__'):
                return False
            return True
        if hidden and virtual and regex is None and not alias:
            return list(self.column_names)  # quick path
        if not hidden and virtual and regex is None and not alias:
            return [k for k in self.column_names if not k.startswith('__')]  # also a quick path
        return [aliases_reverse.get(name, name) for name in self.column_names if column_filter(name)]