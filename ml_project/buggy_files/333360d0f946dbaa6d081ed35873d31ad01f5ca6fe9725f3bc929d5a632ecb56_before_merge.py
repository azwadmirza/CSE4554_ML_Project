def _extract_nc4_variable_encoding(variable, raise_on_invalid=False,
                                   lsd_okay=True, h5py_okay=False,
                                   backend='netCDF4', unlimited_dims=None):
    if unlimited_dims is None:
        unlimited_dims = ()

    encoding = variable.encoding.copy()

    safe_to_drop = set(['source', 'original_shape'])
    valid_encodings = set(['zlib', 'complevel', 'fletcher32', 'contiguous',
                           'chunksizes', 'shuffle', '_FillValue', 'dtype'])
    if lsd_okay:
        valid_encodings.add('least_significant_digit')
    if h5py_okay:
        valid_encodings.add('compression')
        valid_encodings.add('compression_opts')

    if not raise_on_invalid and encoding.get('chunksizes') is not None:
        # It's possible to get encoded chunksizes larger than a dimension size
        # if the original file had an unlimited dimension. This is problematic
        # if the new file no longer has an unlimited dimension.
        chunksizes = encoding['chunksizes']
        chunks_too_big = any(
            c > d and dim not in unlimited_dims
            for c, d, dim in zip(chunksizes, variable.shape, variable.dims))
        changed_shape = encoding.get('original_shape') != variable.shape
        if chunks_too_big or changed_shape:
            del encoding['chunksizes']

    for k in safe_to_drop:
        if k in encoding:
            del encoding[k]

    if raise_on_invalid:
        invalid = [k for k in encoding if k not in valid_encodings]
        if invalid:
            raise ValueError(
                'unexpected encoding parameters for %r backend: %r. Valid '
                'encodings are: %r' % (backend, invalid, valid_encodings))
    else:
        for k in list(encoding):
            if k not in valid_encodings:
                del encoding[k]

    return encoding