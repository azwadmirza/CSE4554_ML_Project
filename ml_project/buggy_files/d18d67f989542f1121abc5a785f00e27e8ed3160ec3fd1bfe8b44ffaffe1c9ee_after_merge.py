def _ensure_plottable(*args):
    """
    Raise exception if there is anything in args that can't be plotted on an
    axis by matplotlib.
    """
    numpy_types = [np.floating, np.integer, np.timedelta64, np.datetime64, np.bool_]
    other_types = [datetime]
    try:
        import cftime

        cftime_datetime = [cftime.datetime]
    except ImportError:
        cftime_datetime = []
    other_types = other_types + cftime_datetime
    for x in args:
        if not (
            _valid_numpy_subdtype(np.array(x), numpy_types)
            or _valid_other_type(np.array(x), other_types)
        ):
            raise TypeError(
                "Plotting requires coordinates to be numeric, boolean, "
                "or dates of type numpy.datetime64, "
                "datetime.datetime, cftime.datetime or "
                f"pandas.Interval. Received data of type {np.array(x).dtype} instead."
            )
        if (
            _valid_other_type(np.array(x), cftime_datetime)
            and not nc_time_axis_available
        ):
            raise ImportError(
                "Plotting of arrays of cftime.datetime "
                "objects or arrays indexed by "
                "cftime.datetime objects requires the "
                "optional `nc-time-axis` (v1.2.0 or later) "
                "package."
            )