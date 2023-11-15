def decode_cf_timedelta(num_timedeltas, units):
    """Given an array of numeric timedeltas in netCDF format, convert it into a
    numpy timedelta64[ns] array.
    """
    num_timedeltas = np.asarray(num_timedeltas)
    units = _netcdf_to_numpy_timeunit(units)

    shape = num_timedeltas.shape
    num_timedeltas = num_timedeltas.ravel()

    result = pd.to_timedelta(num_timedeltas, unit=units, box=False)
    # NaT is returned unboxed with wrong units; this should be fixed in pandas
    if result.dtype != 'timedelta64[ns]':
        result = result.astype('timedelta64[ns]')
    return result.reshape(shape)