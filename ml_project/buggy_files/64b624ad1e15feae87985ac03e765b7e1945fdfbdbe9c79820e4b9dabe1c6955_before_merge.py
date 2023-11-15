    def replace(
        self,
        to_replace=None,
        value=None,
        inplace: bool_t = False,
        limit: Optional[int] = None,
        regex=False,
        method="pad",
    ):
        """
        Replace values given in `to_replace` with `value`.

        Values of the {klass} are replaced with other values dynamically.
        This differs from updating with ``.loc`` or ``.iloc``, which require
        you to specify a location to update with some value.

        Parameters
        ----------
        to_replace : str, regex, list, dict, Series, int, float, or None
            How to find the values that will be replaced.

            * numeric, str or regex:

                - numeric: numeric values equal to `to_replace` will be
                  replaced with `value`
                - str: string exactly matching `to_replace` will be replaced
                  with `value`
                - regex: regexs matching `to_replace` will be replaced with
                  `value`

            * list of str, regex, or numeric:

                - First, if `to_replace` and `value` are both lists, they
                  **must** be the same length.
                - Second, if ``regex=True`` then all of the strings in **both**
                  lists will be interpreted as regexs otherwise they will match
                  directly. This doesn't matter much for `value` since there
                  are only a few possible substitution regexes you can use.
                - str, regex and numeric rules apply as above.

            * dict:

                - Dicts can be used to specify different replacement values
                  for different existing values. For example,
                  ``{{'a': 'b', 'y': 'z'}}`` replaces the value 'a' with 'b' and
                  'y' with 'z'. To use a dict in this way the `value`
                  parameter should be `None`.
                - For a DataFrame a dict can specify that different values
                  should be replaced in different columns. For example,
                  ``{{'a': 1, 'b': 'z'}}`` looks for the value 1 in column 'a'
                  and the value 'z' in column 'b' and replaces these values
                  with whatever is specified in `value`. The `value` parameter
                  should not be ``None`` in this case. You can treat this as a
                  special case of passing two lists except that you are
                  specifying the column to search in.
                - For a DataFrame nested dictionaries, e.g.,
                  ``{{'a': {{'b': np.nan}}}}``, are read as follows: look in column
                  'a' for the value 'b' and replace it with NaN. The `value`
                  parameter should be ``None`` to use a nested dict in this
                  way. You can nest regular expressions as well. Note that
                  column names (the top-level dictionary keys in a nested
                  dictionary) **cannot** be regular expressions.

            * None:

                - This means that the `regex` argument must be a string,
                  compiled regular expression, or list, dict, ndarray or
                  Series of such elements. If `value` is also ``None`` then
                  this **must** be a nested dictionary or Series.

            See the examples section for examples of each of these.
        value : scalar, dict, list, str, regex, default None
            Value to replace any values matching `to_replace` with.
            For a DataFrame a dict of values can be used to specify which
            value to use for each column (columns not in the dict will not be
            filled). Regular expressions, strings and lists or dicts of such
            objects are also allowed.
        inplace : bool, default False
            If True, in place. Note: this will modify any
            other views on this object (e.g. a column from a DataFrame).
            Returns the caller if this is True.
        limit : int or None, default None
            Maximum size gap to forward or backward fill.
        regex : bool or same types as `to_replace`, default False
            Whether to interpret `to_replace` and/or `value` as regular
            expressions. If this is ``True`` then `to_replace` *must* be a
            string. Alternatively, this could be a regular expression or a
            list, dict, or array of regular expressions in which case
            `to_replace` must be ``None``.
        method : {{'pad', 'ffill', 'bfill', `None`}}
            The method to use when for replacement, when `to_replace` is a
            scalar, list or tuple and `value` is ``None``.

            .. versionchanged:: 0.23.0
                Added to DataFrame.

        Returns
        -------
        {klass}
            Object after replacement.

        Raises
        ------
        AssertionError
            * If `regex` is not a ``bool`` and `to_replace` is not
              ``None``.

        TypeError
            * If `to_replace` is not a scalar, array-like, ``dict``, or ``None``
            * If `to_replace` is a ``dict`` and `value` is not a ``list``,
              ``dict``, ``ndarray``, or ``Series``
            * If `to_replace` is ``None`` and `regex` is not compilable
              into a regular expression or is a list, dict, ndarray, or
              Series.
            * When replacing multiple ``bool`` or ``datetime64`` objects and
              the arguments to `to_replace` does not match the type of the
              value being replaced

        ValueError
            * If a ``list`` or an ``ndarray`` is passed to `to_replace` and
              `value` but they are not the same length.

        See Also
        --------
        {klass}.fillna : Fill NA values.
        {klass}.where : Replace values based on boolean condition.
        Series.str.replace : Simple string replacement.

        Notes
        -----
        * Regex substitution is performed under the hood with ``re.sub``. The
          rules for substitution for ``re.sub`` are the same.
        * Regular expressions will only substitute on strings, meaning you
          cannot provide, for example, a regular expression matching floating
          point numbers and expect the columns in your frame that have a
          numeric dtype to be matched. However, if those floating point
          numbers *are* strings, then you can do this.
        * This method has *a lot* of options. You are encouraged to experiment
          and play with this method to gain intuition about how it works.
        * When dict is used as the `to_replace` value, it is like
          key(s) in the dict are the to_replace part and
          value(s) in the dict are the value parameter.

        Examples
        --------

        **Scalar `to_replace` and `value`**

        >>> s = pd.Series([0, 1, 2, 3, 4])
        >>> s.replace(0, 5)
        0    5
        1    1
        2    2
        3    3
        4    4
        dtype: int64

        >>> df = pd.DataFrame({{'A': [0, 1, 2, 3, 4],
        ...                    'B': [5, 6, 7, 8, 9],
        ...                    'C': ['a', 'b', 'c', 'd', 'e']}})
        >>> df.replace(0, 5)
           A  B  C
        0  5  5  a
        1  1  6  b
        2  2  7  c
        3  3  8  d
        4  4  9  e

        **List-like `to_replace`**

        >>> df.replace([0, 1, 2, 3], 4)
           A  B  C
        0  4  5  a
        1  4  6  b
        2  4  7  c
        3  4  8  d
        4  4  9  e

        >>> df.replace([0, 1, 2, 3], [4, 3, 2, 1])
           A  B  C
        0  4  5  a
        1  3  6  b
        2  2  7  c
        3  1  8  d
        4  4  9  e

        >>> s.replace([1, 2], method='bfill')
        0    0
        1    3
        2    3
        3    3
        4    4
        dtype: int64

        **dict-like `to_replace`**

        >>> df.replace({{0: 10, 1: 100}})
             A  B  C
        0   10  5  a
        1  100  6  b
        2    2  7  c
        3    3  8  d
        4    4  9  e

        >>> df.replace({{'A': 0, 'B': 5}}, 100)
             A    B  C
        0  100  100  a
        1    1    6  b
        2    2    7  c
        3    3    8  d
        4    4    9  e

        >>> df.replace({{'A': {{0: 100, 4: 400}}}})
             A  B  C
        0  100  5  a
        1    1  6  b
        2    2  7  c
        3    3  8  d
        4  400  9  e

        **Regular expression `to_replace`**

        >>> df = pd.DataFrame({{'A': ['bat', 'foo', 'bait'],
        ...                    'B': ['abc', 'bar', 'xyz']}})
        >>> df.replace(to_replace=r'^ba.$', value='new', regex=True)
              A    B
        0   new  abc
        1   foo  new
        2  bait  xyz

        >>> df.replace({{'A': r'^ba.$'}}, {{'A': 'new'}}, regex=True)
              A    B
        0   new  abc
        1   foo  bar
        2  bait  xyz

        >>> df.replace(regex=r'^ba.$', value='new')
              A    B
        0   new  abc
        1   foo  new
        2  bait  xyz

        >>> df.replace(regex={{r'^ba.$': 'new', 'foo': 'xyz'}})
              A    B
        0   new  abc
        1   xyz  new
        2  bait  xyz

        >>> df.replace(regex=[r'^ba.$', 'foo'], value='new')
              A    B
        0   new  abc
        1   new  new
        2  bait  xyz

        Note that when replacing multiple ``bool`` or ``datetime64`` objects,
        the data types in the `to_replace` parameter must match the data
        type of the value being replaced:

        >>> df = pd.DataFrame({{'A': [True, False, True],
        ...                    'B': [False, True, False]}})
        >>> df.replace({{'a string': 'new value', True: False}})  # raises
        Traceback (most recent call last):
            ...
        TypeError: Cannot compare types 'ndarray(dtype=bool)' and 'str'

        This raises a ``TypeError`` because one of the ``dict`` keys is not of
        the correct type for replacement.

        Compare the behavior of ``s.replace({{'a': None}})`` and
        ``s.replace('a', None)`` to understand the peculiarities
        of the `to_replace` parameter:

        >>> s = pd.Series([10, 'a', 'a', 'b', 'a'])

        When one uses a dict as the `to_replace` value, it is like the
        value(s) in the dict are equal to the `value` parameter.
        ``s.replace({{'a': None}})`` is equivalent to
        ``s.replace(to_replace={{'a': None}}, value=None, method=None)``:

        >>> s.replace({{'a': None}})
        0      10
        1    None
        2    None
        3       b
        4    None
        dtype: object

        When ``value=None`` and `to_replace` is a scalar, list or
        tuple, `replace` uses the method parameter (default 'pad') to do the
        replacement. So this is why the 'a' values are being replaced by 10
        in rows 1 and 2 and 'b' in row 4 in this case.
        The command ``s.replace('a', None)`` is actually equivalent to
        ``s.replace(to_replace='a', value=None, method='pad')``:

        >>> s.replace('a', None)
        0    10
        1    10
        2    10
        3     b
        4     b
        dtype: object
        """
        if not (
            is_scalar(to_replace)
            or is_re_compilable(to_replace)
            or is_list_like(to_replace)
        ):
            raise TypeError(
                "Expecting 'to_replace' to be either a scalar, array-like, "
                "dict or None, got invalid type "
                f"{repr(type(to_replace).__name__)}"
            )

        inplace = validate_bool_kwarg(inplace, "inplace")
        if not is_bool(regex) and to_replace is not None:
            raise ValueError("'to_replace' must be 'None' if 'regex' is not a bool")

        if value is None:
            # passing a single value that is scalar like
            # when value is None (GH5319), for compat
            if not is_dict_like(to_replace) and not is_dict_like(regex):
                to_replace = [to_replace]

            if isinstance(to_replace, (tuple, list)):
                if isinstance(self, ABCDataFrame):
                    return self.apply(
                        _single_replace, args=(to_replace, method, inplace, limit)
                    )
                return _single_replace(self, to_replace, method, inplace, limit)

            if not is_dict_like(to_replace):
                if not is_dict_like(regex):
                    raise TypeError(
                        'If "to_replace" and "value" are both None '
                        'and "to_replace" is not a list, then '
                        "regex must be a mapping"
                    )
                to_replace = regex
                regex = True

            items = list(to_replace.items())
            if items:
                keys, values = zip(*items)
            else:
                keys, values = ([], [])

            are_mappings = [is_dict_like(v) for v in values]

            if any(are_mappings):
                if not all(are_mappings):
                    raise TypeError(
                        "If a nested mapping is passed, all values "
                        "of the top level mapping must be mappings"
                    )
                # passed a nested dict/Series
                to_rep_dict = {}
                value_dict = {}

                for k, v in items:
                    keys, values = list(zip(*v.items())) or ([], [])

                    to_rep_dict[k] = list(keys)
                    value_dict[k] = list(values)

                to_replace, value = to_rep_dict, value_dict
            else:
                to_replace, value = keys, values

            return self.replace(
                to_replace, value, inplace=inplace, limit=limit, regex=regex
            )
        else:

            # need a non-zero len on all axes
            if not self.size:
                if inplace:
                    return
                return self.copy()

            if is_dict_like(to_replace):
                if is_dict_like(value):  # {'A' : NA} -> {'A' : 0}
                    # Note: Checking below for `in foo.keys()` instead of
                    #  `in foo` is needed for when we have a Series and not dict
                    mapping = {
                        col: (to_replace[col], value[col])
                        for col in to_replace.keys()
                        if col in value.keys() and col in self
                    }
                    return self._replace_columnwise(mapping, inplace, regex)

                # {'A': NA} -> 0
                elif not is_list_like(value):
                    # Operate column-wise
                    if self.ndim == 1:
                        raise ValueError(
                            "Series.replace cannot use dict-like to_replace "
                            "and non-None value"
                        )
                    mapping = {
                        col: (to_rep, value) for col, to_rep in to_replace.items()
                    }
                    return self._replace_columnwise(mapping, inplace, regex)
                else:
                    raise TypeError("value argument must be scalar, dict, or Series")

            elif is_list_like(to_replace):  # [NA, ''] -> [0, 'missing']
                if is_list_like(value):
                    if len(to_replace) != len(value):
                        raise ValueError(
                            f"Replacement lists must match in length. "
                            f"Expecting {len(to_replace)} got {len(value)} "
                        )
                    self._consolidate_inplace()
                    new_data = self._mgr.replace_list(
                        src_list=to_replace,
                        dest_list=value,
                        inplace=inplace,
                        regex=regex,
                    )

                else:  # [NA, ''] -> 0
                    new_data = self._mgr.replace(
                        to_replace=to_replace, value=value, inplace=inplace, regex=regex
                    )
            elif to_replace is None:
                if not (
                    is_re_compilable(regex)
                    or is_list_like(regex)
                    or is_dict_like(regex)
                ):
                    raise TypeError(
                        f"'regex' must be a string or a compiled regular expression "
                        f"or a list or dict of strings or regular expressions, "
                        f"you passed a {repr(type(regex).__name__)}"
                    )
                return self.replace(
                    regex, value, inplace=inplace, limit=limit, regex=True
                )
            else:

                # dest iterable dict-like
                if is_dict_like(value):  # NA -> {'A' : 0, 'B' : -1}
                    # Operate column-wise
                    if self.ndim == 1:
                        raise ValueError(
                            "Series.replace cannot use dict-value and "
                            "non-None to_replace"
                        )
                    mapping = {col: (to_replace, val) for col, val in value.items()}
                    return self._replace_columnwise(mapping, inplace, regex)

                elif not is_list_like(value):  # NA -> 0
                    new_data = self._mgr.replace(
                        to_replace=to_replace, value=value, inplace=inplace, regex=regex
                    )
                else:
                    raise TypeError(
                        f'Invalid "to_replace" type: {repr(type(to_replace).__name__)}'
                    )

        result = self._constructor(new_data)
        if inplace:
            return self._update_inplace(result)
        else:
            return result.__finalize__(self, method="replace")