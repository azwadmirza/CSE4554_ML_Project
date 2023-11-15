    def __init__(
        self, data=None, index=None, dtype=None, name=None, copy=False, fastpath=False
    ):
        # we are called internally, so short-circuit
        if fastpath:

            # data is an ndarray, index is defined
            if not isinstance(data, SingleBlockManager):
                data = SingleBlockManager(data, index, fastpath=True)
            if copy:
                data = data.copy()
            if index is None:
                index = data.index

        else:

            if is_empty_data(data) and dtype is None:
                # gh-17261
                warnings.warn(
                    "The default dtype for empty Series will be 'object' instead "
                    "of 'float64' in a future version. Specify a dtype explicitly "
                    "to silence this warning.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                # uncomment the line below when removing the DeprecationWarning
                # dtype = np.dtype(object)

            if index is not None:
                index = ensure_index(index)

            if data is None:
                data = {}
            if dtype is not None:
                dtype = self._validate_dtype(dtype)

            if isinstance(data, MultiIndex):
                raise NotImplementedError(
                    "initializing a Series from a MultiIndex is not supported"
                )
            elif isinstance(data, Index):
                if name is None:
                    name = data.name

                if dtype is not None:
                    # astype copies
                    data = data.astype(dtype)
                else:
                    # need to copy to avoid aliasing issues
                    data = data._values.copy()
                    if isinstance(data, ABCDatetimeIndex) and data.tz is not None:
                        # GH#24096 need copy to be deep for datetime64tz case
                        # TODO: See if we can avoid these copies
                        data = data._values.copy(deep=True)
                copy = False

            elif isinstance(data, np.ndarray):
                if len(data.dtype):
                    # GH#13296 we are dealing with a compound dtype, which
                    #  should be treated as 2D
                    raise ValueError(
                        "Cannot construct a Series from an ndarray with "
                        "compound dtype.  Use DataFrame instead."
                    )
                pass
            elif isinstance(data, ABCSeries):
                if name is None:
                    name = data.name
                if index is None:
                    index = data.index
                else:
                    data = data.reindex(index, copy=copy)
                data = data._data
            elif isinstance(data, dict):
                data, index = self._init_dict(data, index, dtype)
                dtype = None
                copy = False
            elif isinstance(data, SingleBlockManager):
                if index is None:
                    index = data.index
                elif not data.index.equals(index) or copy:
                    # GH#19275 SingleBlockManager input should only be called
                    # internally
                    raise AssertionError(
                        "Cannot pass both SingleBlockManager "
                        "`data` argument and a different "
                        "`index` argument. `copy` must be False."
                    )

            elif is_extension_array_dtype(data):
                pass
            elif isinstance(data, (set, frozenset)):
                raise TypeError(f"'{type(data).__name__}' type is unordered")
            elif isinstance(data, ABCSparseArray):
                # handle sparse passed here (and force conversion)
                data = data.to_dense()
            else:
                data = com.maybe_iterable_to_list(data)

            if index is None:
                if not is_list_like(data):
                    data = [data]
                index = ibase.default_index(len(data))
            elif is_list_like(data):

                # a scalar numpy array is list-like but doesn't
                # have a proper length
                try:
                    if len(index) != len(data):
                        raise ValueError(
                            f"Length of passed values is {len(data)}, "
                            f"index implies {len(index)}."
                        )
                except TypeError:
                    pass

            # create/copy the manager
            if isinstance(data, SingleBlockManager):
                if dtype is not None:
                    data = data.astype(dtype=dtype, errors="ignore", copy=copy)
                elif copy:
                    data = data.copy()
            else:
                data = sanitize_array(data, index, dtype, copy, raise_cast_failure=True)

                data = SingleBlockManager(data, index, fastpath=True)

        generic.NDFrame.__init__(self, data, fastpath=True)
        self.name = name
        self._set_axis(0, index, fastpath=True)