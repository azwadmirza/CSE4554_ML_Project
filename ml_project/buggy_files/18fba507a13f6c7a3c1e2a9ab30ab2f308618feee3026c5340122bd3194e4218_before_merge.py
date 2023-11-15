def open_dataset(filename_or_obj, group=None, decode_cf=True,
                 mask_and_scale=True, decode_times=True,
                 concat_characters=True, decode_coords=True):
    """Load and decode a dataset from a file or file-like object.

    Parameters
    ----------
    filename_or_obj : str or file
        Strings are interpreted as a path to a netCDF file or an OpenDAP URL
        and opened with python-netCDF4, unless the filename ends with .gz, in
        which case the file is gunzipped and opened with scipy.io.netcdf (only
        netCDF3 supported). File-like objects are opened with scipy.io.netcdf
        (only netCDF3 supported).
    group : str, optional
        Path to the netCDF4 group in the given file to open (only works for
        netCDF4 files).
    decode_cf : bool, optional
        Whether to decode these variables, assuming they were saved according
        to CF conventions.
    mask_and_scale : bool, optional
        If True, replace array values equal to `_FillValue` with NA and scale
        values according to the formula `original_values * scale_factor +
        add_offset`, where `_FillValue`, `scale_factor` and `add_offset` are
        taken from variable attributes (if they exist).
    decode_times : bool, optional
        If True, decode times encoded in the standard NetCDF datetime format
        into datetime objects. Otherwise, leave them encoded as numbers.
    concat_characters : bool, optional
        If True, concatenate along the last dimension of character arrays to
        form string arrays. Dimensions will only be concatenated over (and
        removed) if they have no corresponding variable and if they are only
        used as the last dimension of character arrays.
    decode_coords : bool, optional
        If True, decode the 'coordinates' attribute to identify coordinates in
        the resulting dataset.

    Returns
    -------
    dataset : Dataset
        The newly created dataset.
    """
    if isinstance(filename_or_obj, basestring):
        if filename_or_obj.endswith('.gz'):
            # if the string ends with .gz, then gunzip and open as netcdf file
            if sys.version_info[:2] < (2, 7):
                raise ValueError('reading a gzipped netCDF not '
                                 'supported on Python 2.6')
            try:
                store = backends.ScipyDataStore(gzip.open(filename_or_obj))
            except TypeError as e:
                # TODO: gzipped loading only works with NetCDF3 files.
                if 'is not a valid NetCDF 3 file' in e.message:
                    raise ValueError('gzipped file loading only supports '
                                     'NetCDF 3 files.')
                else:
                    raise
        else:
            try:
                store = backends.NetCDF4DataStore(filename_or_obj, group=group)
            except ImportError:
                store = backends.ScipyDataStore(filename_or_obj)
    else:
        # assume filename_or_obj is a file-like object
        store = backends.ScipyDataStore(filename_or_obj)

    if decode_cf:
        return conventions.decode_cf(
            store, mask_and_scale=mask_and_scale,
            decode_times=decode_times, concat_characters=concat_characters,
            decode_coords=decode_coords)
    else:
        return Dataset.load_store(store)