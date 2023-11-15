def basic_computations(df: dd.DataFrame) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Computations for the basic version.

    Parameters
    ----------
    df
        The DataFrame for which data are calculated.
    """
    data: Dict[str, Any] = {}
    df = DataArray(df)

    df_num = df.select_num_columns()
    data["num_cols"] = df_num.columns
    first_rows = df.select_dtypes(CATEGORICAL_DTYPES).head

    # variables
    for col in df.columns:
        if is_dtype(detect_dtype(df.frame[col]), Continuous()):
            data[col] = cont_comps(df.frame[col], 20)
        elif is_dtype(detect_dtype(df.frame[col]), Nominal()):
            # cast the column as string type if it contains a mutable type
            try:
                first_rows[col].apply(hash)
            except TypeError:
                df.frame[col] = df.frame[col].astype(str)
            data[col] = nom_comps(
                df.frame[col], first_rows[col], 10, True, 10, 20, True, False, False
            )
        elif is_dtype(detect_dtype(df.frame[col]), DateTime()):
            data[col] = {}
            data[col]["stats"] = calc_stats_dt(df.frame[col])
            data[col]["line"] = dask.delayed(_calc_line_dt)(df.frame[[col]], "auto")

    # overview
    data["ov"] = calc_stats(df.frame, None)
    # interactions
    data["scat"] = df_num.frame.map_partitions(
        lambda x: x.sample(min(1000, x.shape[0])), meta=df_num.frame
    )
    # correlations
    data.update(zip(("cordx", "cordy", "corrs"), correlation_nxn(df_num)))
    # missing values
    (delayed, completion,) = compute_missing_nullivariate(  # pylint: disable=unexpected-keyword-arg
        df, 30, _staged=True
    )
    data["miss"] = delayed
    completions = {"miss": completion}

    return data, completions