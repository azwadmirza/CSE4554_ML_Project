def _yt_array_hdf5_attr(fh, attr, val):
    r"""Save a YTArray or YTQuantity as an hdf5 attribute.

    Save an hdf5 attribute.  If it has units, save an
    additional attribute with the units.

    Parameters
    ----------
    fh : an open hdf5 file, group, or dataset
        The hdf5 file, group, or dataset to which the
        attribute will be written.
    attr : str
        The name of the attribute to be saved.
    val : anything
        The value to be saved.

    """

    if val is None: val = "None"
    if hasattr(val, "units"):
        fh.attrs["%s_units" % attr] = str(val.units)
    # The following is a crappy workaround for getting
    # Unicode strings into HDF5 attributes in Python 3
    if iterable(val):
        val = np.array(val)
        if val.dtype.kind == 'U':
            val = val.astype('|S')
    try:
        fh.attrs[str(attr)] = val
    # This is raised if no HDF5 equivalent exists.
    # In that case, save its string representation.
    except TypeError:
        fh.attrs[str(attr)] = str(val)