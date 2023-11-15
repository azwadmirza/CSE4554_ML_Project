def histogram(
    srs: dd.Series,
    bins: Optional[int] = None,
    return_edges: bool = True,
    range: Optional[Tuple[int, int]] = None,  # pylint: disable=redefined-builtin
    dtype: Optional[DTypeDef] = None,
) -> Union[Tuple[da.Array, da.Array], Tuple[da.Array, da.Array, da.Array]]:
    """
    Calculate histogram for both numerical and categorical
    """

    if is_dtype(detect_dtype(srs, dtype), Continuous()):
        if range is not None:
            minimum, maximum = range
        else:
            minimum, maximum = srs.min(axis=0), srs.max(axis=0)
        minimum, maximum = dask.compute(minimum, maximum)

        assert (
            bins is not None
        ), "num_bins cannot be None if calculating numerical histograms"

        counts, edges = da.histogram(
            srs.to_dask_array(), bins, range=[minimum, maximum]
        )
        centers = (edges[:-1] + edges[1:]) / 2

        if not return_edges:
            return counts, centers
        return counts, centers, edges
    elif is_dtype(detect_dtype(srs, dtype), Nominal()):
        value_counts = srs.value_counts()
        counts = value_counts.to_dask_array()

        # Dask array dones't understand the pandas dtypes such as categorical type.
        # We convert these types into str before calling into `to_dask_array`.

        if is_pandas_categorical(value_counts.index.dtype):
            centers = value_counts.index.astype("str").to_dask_array()
        else:
            centers = value_counts.index.to_dask_array()
        return (counts, centers)
    else:
        raise UnreachableError()