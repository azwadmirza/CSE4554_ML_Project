    def to_dict(self, orient='dict', into=dict):
        """Convert DataFrame to dictionary.

        Parameters
        ----------
        orient : str {'dict', 'list', 'series', 'split', 'records', 'index'}
            Determines the type of the values of the dictionary.

            - dict (default) : dict like {column -> {index -> value}}
            - list : dict like {column -> [values]}
            - series : dict like {column -> Series(values)}
            - split : dict like
              {index -> [index], columns -> [columns], data -> [values]}
            - records : list like
              [{column -> value}, ... , {column -> value}]
            - index : dict like {index -> {column -> value}}

              .. versionadded:: 0.17.0

            Abbreviations are allowed. `s` indicates `series` and `sp`
            indicates `split`.

        into : class, default dict
            The collections.Mapping subclass used for all Mappings
            in the return value.  Can be the actual class or an empty
            instance of the mapping type you want.  If you want a
            collections.defaultdict, you must pass it initialized.

            .. versionadded:: 0.21.0

        Returns
        -------
        result : collections.Mapping like {column -> {index -> value}}

        Examples
        --------
        >>> df = pd.DataFrame(
                {'col1': [1, 2], 'col2': [0.5, 0.75]}, index=['a', 'b'])
        >>> df
           col1  col2
        a     1   0.1
        b     2   0.2
        >>> df.to_dict()
        {'col1': {'a': 1, 'b': 2}, 'col2': {'a': 0.5, 'b': 0.75}}

        You can specify the return orientation.

        >>> df.to_dict('series')
        {'col1': a    1
        b    2
        Name: col1, dtype: int64, 'col2': a    0.50
        b    0.75
        Name: col2, dtype: float64}
        >>> df.to_dict('split')
        {'columns': ['col1', 'col2'],
        'data': [[1.0, 0.5], [2.0, 0.75]],
        'index': ['a', 'b']}
        >>> df.to_dict('records')
        [{'col1': 1.0, 'col2': 0.5}, {'col1': 2.0, 'col2': 0.75}]
        >>> df.to_dict('index')
        {'a': {'col1': 1.0, 'col2': 0.5}, 'b': {'col1': 2.0, 'col2': 0.75}}

        You can also specify the mapping type.

        >>> from collections import OrderedDict, defaultdict
        >>> df.to_dict(into=OrderedDict)
        OrderedDict([('col1', OrderedDict([('a', 1), ('b', 2)])),
                   ('col2', OrderedDict([('a', 0.5), ('b', 0.75)]))])

        If you want a `defaultdict`, you need to initialize it:

        >>> dd = defaultdict(list)
        >>> df.to_dict('records', into=dd)
        [defaultdict(<type 'list'>, {'col2': 0.5, 'col1': 1.0}),
        defaultdict(<type 'list'>, {'col2': 0.75, 'col1': 2.0})]
        """
        if not self.columns.is_unique:
            warnings.warn("DataFrame columns are not unique, some "
                          "columns will be omitted.", UserWarning,
                          stacklevel=2)
        # GH16122
        into_c = standardize_mapping(into)
        if orient.lower().startswith('d'):
            return into_c(
                (k, v.to_dict(into)) for k, v in compat.iteritems(self))
        elif orient.lower().startswith('l'):
            return into_c((k, v.tolist()) for k, v in compat.iteritems(self))
        elif orient.lower().startswith('sp'):
            return into_c((('index', self.index.tolist()),
                           ('columns', self.columns.tolist()),
                           ('data', lib.map_infer(self.values.ravel(),
                                                  _maybe_box_datetimelike)
                            .reshape(self.values.shape).tolist())))
        elif orient.lower().startswith('s'):
            return into_c((k, _maybe_box_datetimelike(v))
                          for k, v in compat.iteritems(self))
        elif orient.lower().startswith('r'):
            return [into_c((k, _maybe_box_datetimelike(v))
                           for k, v in zip(self.columns, np.atleast_1d(row)))
                    for row in self.values]
        elif orient.lower().startswith('i'):
            return into_c((k, v.to_dict(into)) for k, v in self.iterrows())
        else:
            raise ValueError("orient '%s' not understood" % orient)