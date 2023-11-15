def missing_spectrum(
    df: dd.DataFrame, bins: int, ncols: int
) -> Tuple[dd.DataFrame, dd.DataFrame]:
    """
    Calculate a missing spectrum for each column
    """
    # pylint: disable=too-many-locals
    num_bins = min(bins, len(df) - 1)

    df = df.iloc[:, :ncols]
    cols = df.columns[:ncols]
    ncols = len(cols)
    nrows = len(df)
    chunk_size = len(df) // num_bins
    data = df.isnull().to_dask_array()
    data.compute_chunk_sizes()
    data = data.rechunk((chunk_size, None))

    notnull_counts = data.sum(axis=0) / data.shape[0]
    total_missing_percs = {col: notnull_counts[idx] for idx, col in enumerate(cols)}

    spectrum_missing_percs = data.map_blocks(
        missing_perc_blockwise, chunks=(1, data.shape[1]), dtype=float
    )
    nsegments = len(spectrum_missing_percs)

    locs0 = da.arange(nsegments) * chunk_size
    locs1 = da.minimum(locs0 + chunk_size, nrows)
    locs_middle = locs0 + chunk_size / 2

    df = dd.from_dask_array(
        da.repeat(da.from_array(cols.values, (1,)), nsegments), columns=["column"],
    )

    df = df.assign(
        location=da.tile(locs_middle, ncols),
        missing_rate=spectrum_missing_percs.T.ravel(),
        loc_start=da.tile(locs0, ncols),
        loc_end=da.tile(locs1, ncols),
    )

    return df, total_missing_percs