def file_reader(filename, select_type=None, index=0, downsample=1,     # noqa
                cutoff_at_kV=None, instrument=None, lazy=False):
    """Reads a bruker bcf file and loads the data into the appropriate class,
    then wraps it into appropriate hyperspy required list of dictionaries
    used by hyperspy.api.load() method.

    Keyword arguments:
    select_type -- One of: spectrum, image. If none specified, then function
      loads everything, else if specified, loads either just sem imagery,
      or just hyper spectral mapping data. (default None)
    index -- index of dataset in bcf v2 (delaut 0)
    downsample -- the downsample ratio of hyperspectral array (downsampling
      height and width only), can be integer from 1 to inf, where '1' means
      no downsampling will be applied (default 1).
    cutoff_at_kV -- if set (can be int of float >= 0) can be used either, to
       crop or enlarge energy range at max values. (default None)
    instrument -- str, either 'TEM' or 'SEM'. Default is None.
      """

    # objectified bcf file:
    obj_bcf = BCF_reader(filename, instrument=instrument)
    if select_type == 'image':
        return bcf_imagery(obj_bcf)
    elif select_type == 'spectrum':
        return bcf_hyperspectra(obj_bcf, index=index,
                                downsample=downsample,
                                cutoff_at_kV=cutoff_at_kV,
                                lazy=lazy)
    else:
        return bcf_imagery(obj_bcf) + bcf_hyperspectra(
            obj_bcf,
            index=index,
            downsample=downsample,
            cutoff_at_kV=cutoff_at_kV,
            lazy=lazy)