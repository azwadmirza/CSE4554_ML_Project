    def __init__(
        self,
        data=None,
        index: Optional[Axes] = None,
        columns: Optional[Axes] = None,
        dtype: Optional[Dtype] = None,
        copy: bool = False,
    ):
        if data is None:
            data = {}
        if dtype is not None:
            dtype = self._validate_dtype(dtype)

        if isinstance(data, DataFrame):
            data = data._mgr

        if isinstance(data, BlockManager):
            if index is None and columns is None and dtype is None and copy is False:
                # GH#33357 fastpath
                NDFrame.__init__(self, data)
                return

            mgr = self._init_mgr(
                data, axes={"index": index, "columns": columns}, dtype=dtype, copy=copy
            )

        elif isinstance(data, dict):
            mgr = init_dict(data, index, columns, dtype=dtype)
        elif isinstance(data, ma.MaskedArray):
            import numpy.ma.mrecords as mrecords

            # masked recarray
            if isinstance(data, mrecords.MaskedRecords):
                mgr = masked_rec_array_to_mgr(data, index, columns, dtype, copy)

            # a masked array
            else:
                data = sanitize_masked_array(data)
                mgr = init_ndarray(data, index, columns, dtype=dtype, copy=copy)

        elif isinstance(data, (np.ndarray, Series, Index)):
            if data.dtype.names:
                data_columns = list(data.dtype.names)
                data = {k: data[k] for k in data_columns}
                if columns is None:
                    columns = data_columns
                mgr = init_dict(data, index, columns, dtype=dtype)
            elif getattr(data, "name", None) is not None:
                mgr = init_dict({data.name: data}, index, columns, dtype=dtype)
            else:
                mgr = init_ndarray(data, index, columns, dtype=dtype, copy=copy)

        # For data is list-like, or Iterable (will consume into list)
        elif isinstance(data, abc.Iterable) and not isinstance(data, (str, bytes)):
            if not isinstance(data, (abc.Sequence, ExtensionArray)):
                data = list(data)
            if len(data) > 0:
                if is_dataclass(data[0]):
                    data = dataclasses_to_dicts(data)
                if is_list_like(data[0]) and getattr(data[0], "ndim", 1) == 1:
                    if is_named_tuple(data[0]) and columns is None:
                        columns = data[0]._fields
                    arrays, columns = to_arrays(data, columns, dtype=dtype)
                    columns = ensure_index(columns)

                    # set the index
                    if index is None:
                        if isinstance(data[0], Series):
                            index = get_names_from_index(data)
                        elif isinstance(data[0], Categorical):
                            index = ibase.default_index(len(data[0]))
                        else:
                            index = ibase.default_index(len(data))

                    mgr = arrays_to_mgr(arrays, columns, index, columns, dtype=dtype)
                else:
                    mgr = init_ndarray(data, index, columns, dtype=dtype, copy=copy)
            else:
                mgr = init_dict({}, index, columns, dtype=dtype)
        # For data is scalar
        else:
            if index is None or columns is None:
                raise ValueError("DataFrame constructor not properly called!")

            if not dtype:
                dtype, _ = infer_dtype_from_scalar(data, pandas_dtype=True)

            # For data is a scalar extension dtype
            if is_extension_array_dtype(dtype):

                values = [
                    construct_1d_arraylike_from_scalar(data, len(index), dtype)
                    for _ in range(len(columns))
                ]
                mgr = arrays_to_mgr(values, columns, index, columns, dtype=None)
            else:
                if dtype.kind in ["m", "M"]:
                    data = maybe_unbox_datetimelike(data, dtype)

                # Attempt to coerce to a numpy array
                try:
                    arr = np.array(data, dtype=dtype, copy=copy)
                except (ValueError, TypeError) as err:
                    exc = TypeError(
                        "DataFrame constructor called with "
                        f"incompatible data and dtype: {err}"
                    )
                    raise exc from err

                if arr.ndim != 0:
                    raise ValueError("DataFrame constructor not properly called!")

                shape = (len(index), len(columns))
                values = np.full(shape, arr)

                mgr = init_ndarray(
                    values, index, columns, dtype=values.dtype, copy=False
                )

        NDFrame.__init__(self, mgr)