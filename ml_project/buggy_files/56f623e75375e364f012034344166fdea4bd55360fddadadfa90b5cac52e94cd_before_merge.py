def _dt_prop_map(property_name):
    """
    Create a function that call property of property `dt` of the series.

    Parameters
    ----------
    property_name
        The property of `dt`, which will be applied.

    Returns
    -------
        A callable function to be applied in the partitions

    Notes
    -----
    This applies non-callable properties of `Series.dt`.
    """

    def dt_op_builder(df, *args, **kwargs):
        prop_val = getattr(df.squeeze().dt, property_name)
        if isinstance(prop_val, pandas.Series):
            return prop_val.to_frame()
        else:
            return pandas.DataFrame([prop_val])

    return dt_op_builder