def missing_spectrum(df: dd.DataFrame, bins: int, ncols: int) -> Intermediate:
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

    (notnull_counts,) = dd.compute(data.sum(axis=0) / data.shape[0])
    missing_percent = {col: notnull_counts[idx] for idx, col in enumerate(cols)}

    missing_percs = data.map_blocks(missing_perc_blockwise, dtype=float).compute()
    locs0 = np.arange(len(missing_percs)) * chunk_size
    locs1 = np.minimum(locs0 + chunk_size, nrows)
    locs_middle = locs0 + chunk_size / 2

    df = pd.DataFrame(
        {
            "column": np.repeat(cols.values, len(missing_percs)),
            "location": np.tile(locs_middle, ncols),
            "missing_rate": missing_percs.T.ravel(),
            "loc_start": np.tile(locs0, ncols),
            "loc_end": np.tile(locs1, ncols),
        }
    )
    return Intermediate(
        data=df, missing_percent=missing_percent, visual_type="missing_spectrum",
    )