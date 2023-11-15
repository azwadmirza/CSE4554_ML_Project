    def __init__(
        self,
        obj,
        group,
        squeeze=False,
        grouper=None,
        bins=None,
        restore_coord_dims=None,
        cut_kwargs={},
    ):
        """Create a GroupBy object

        Parameters
        ----------
        obj : Dataset or DataArray
            Object to group.
        group : DataArray
            Array with the group values.
        squeeze : boolean, optional
            If "group" is a coordinate of object, `squeeze` controls whether
            the subarrays have a dimension of length 1 along that coordinate or
            if the dimension is squeezed out.
        grouper : pd.Grouper, optional
            Used for grouping values along the `group` array.
        bins : array-like, optional
            If `bins` is specified, the groups will be discretized into the
            specified bins by `pandas.cut`.
        restore_coord_dims : bool, optional
            If True, also restore the dimension order of multi-dimensional
            coordinates.
        cut_kwargs : dict, optional
            Extra keyword arguments to pass to `pandas.cut`

        """
        from .dataarray import DataArray

        if grouper is not None and bins is not None:
            raise TypeError("can't specify both `grouper` and `bins`")

        if not isinstance(group, (DataArray, IndexVariable)):
            if not hashable(group):
                raise TypeError(
                    "`group` must be an xarray.DataArray or the "
                    "name of an xarray variable or dimension"
                )
            group = obj[group]
            if len(group) == 0:
                raise ValueError(f"{group.name} must not be empty")

            if group.name not in obj.coords and group.name in obj.dims:
                # DummyGroups should not appear on groupby results
                group = _DummyGroup(obj, group.name, group.coords)

        if getattr(group, "name", None) is None:
            raise ValueError("`group` must have a name")

        group, obj, stacked_dim, inserted_dims = _ensure_1d(group, obj)
        group_dim, = group.dims

        expected_size = obj.sizes[group_dim]
        if group.size != expected_size:
            raise ValueError(
                "the group variable's length does not "
                "match the length of this variable along its "
                "dimension"
            )

        full_index = None

        if bins is not None:
            if duck_array_ops.isnull(bins).all():
                raise ValueError("All bin edges are NaN.")
            binned = pd.cut(group.values, bins, **cut_kwargs)
            new_dim_name = group.name + "_bins"
            group = DataArray(binned, group.coords, name=new_dim_name)
            full_index = binned.categories

        if grouper is not None:
            index = safe_cast_to_index(group)
            if not index.is_monotonic:
                # TODO: sort instead of raising an error
                raise ValueError("index must be monotonic for resampling")
            full_index, first_items = self._get_index_and_items(index, grouper)
            sbins = first_items.values.astype(np.int64)
            group_indices = [slice(i, j) for i, j in zip(sbins[:-1], sbins[1:])] + [
                slice(sbins[-1], None)
            ]
            unique_coord = IndexVariable(group.name, first_items.index)
        elif group.dims == (group.name,) and _unique_and_monotonic(group):
            # no need to factorize
            group_indices = np.arange(group.size)
            if not squeeze:
                # use slices to do views instead of fancy indexing
                # equivalent to: group_indices = group_indices.reshape(-1, 1)
                group_indices = [slice(i, i + 1) for i in group_indices]
            unique_coord = group
        else:
            if group.isnull().any():
                # drop any NaN valued groups.
                # also drop obj values where group was NaN
                # Use where instead of reindex to account for duplicate coordinate labels.
                obj = obj.where(group.notnull(), drop=True)
                group = group.dropna(group_dim)

            # look through group to find the unique values
            unique_values, group_indices = unique_value_groups(
                safe_cast_to_index(group), sort=(bins is None)
            )
            unique_coord = IndexVariable(group.name, unique_values)

        if len(group_indices) == 0:
            if bins is not None:
                raise ValueError(
                    "None of the data falls within bins with edges %r" % bins
                )
            else:
                raise ValueError(
                    "Failed to group data. Are you grouping by a variable that is all NaN?"
                )

        if (
            isinstance(obj, DataArray)
            and restore_coord_dims is None
            and any(obj[c].ndim > 1 for c in obj.coords)
        ):
            warnings.warn(
                "This DataArray contains multi-dimensional "
                "coordinates. In the future, the dimension order "
                "of these coordinates will be restored as well "
                "unless you specify restore_coord_dims=False.",
                FutureWarning,
                stacklevel=2,
            )
            restore_coord_dims = False

        # specification for the groupby operation
        self._obj = obj
        self._group = group
        self._group_dim = group_dim
        self._group_indices = group_indices
        self._unique_coord = unique_coord
        self._stacked_dim = stacked_dim
        self._inserted_dims = inserted_dims
        self._full_index = full_index
        self._restore_coord_dims = restore_coord_dims

        # cached attributes
        self._groups = None
        self._dims = None