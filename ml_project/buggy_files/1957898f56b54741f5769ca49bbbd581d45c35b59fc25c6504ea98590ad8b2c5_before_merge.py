def compute_missing(
    # pylint: disable=too-many-arguments
    df: Union[pd.DataFrame, dd.DataFrame],
    x: Optional[str] = None,
    y: Optional[str] = None,
    *,
    bins: int = 30,
    ncols: int = 30,
    ndist_sample: int = 100,
    dtype: Optional[DTypeDef] = None,
) -> Intermediate:
    """
    This function is designed to deal with missing values
    There are three functions: plot_missing(df), plot_missing(df, x)
    plot_missing(df, x, y)

    Parameters
    ----------
    df
        the pandas data_frame for which plots are calculated for each column
    x
        a valid column name of the data frame
    y
        a valid column name of the data frame
    ncols
        The number of columns in the figure
    bins
        The number of rows in the figure
    ndist_sample
        The number of sample points
    dtype: str or DType or dict of str or dict of DType, default None
        Specify Data Types for designated column or all columns.
        E.g.  dtype = {"a": Continuous, "b": "Nominal"} or
        dtype = {"a": Continuous(), "b": "nominal"}
        or dtype = Continuous() or dtype = "Continuous" or dtype = Continuous()
    Examples
    ----------
    >>> from dataprep.eda.missing.computation import plot_missing
    >>> import pandas as pd
    >>> df = pd.read_csv("suicide-rate.csv")
    >>> plot_missing(df, "HDI_for_year")
    >>> plot_missing(df, "HDI_for_year", "population")
    """
    df = to_dask(df)

    # pylint: disable=no-else-raise
    if x is None and y is not None:
        raise ValueError("x cannot be None while y has value")
    elif x is not None and y is None:
        return missing_impact_1vn(df, dtype=dtype, x=x, bins=bins)
    elif x is not None and y is not None:
        return missing_impact_1v1(
            df, dtype=dtype, x=x, y=y, bins=bins, ndist_sample=ndist_sample
        )
    else:
        # return missing_spectrum(df, bins=bins, ncols=ncols)
        return missing_spectrum_tabs(df, bins=bins, ncols=ncols)