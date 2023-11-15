def _extract_nc4_encoding(variable, raise_on_invalid=False, lsd_okay=True,
                          backend='netCDF4'):
    encoding = variable.encoding.copy()

    safe_to_drop = set(['source', 'original_shape'])
    valid_encodings = set(['zlib', 'complevel', 'fletcher32', 'contiguous',
                           'chunksizes'])
    if lsd_okay:
        valid_encodings.add('least_significant_digit')

    if (encoding.get('chunksizes') is not None and
            (encoding.get('original_shape', variable.shape)
             != variable.shape) and
            not raise_on_invalid):
        del encoding['chunksizes']

    for k in safe_to_drop:
        if k in encoding:
            del encoding[k]

    if raise_on_invalid:
        invalid = [k for k in encoding if k not in valid_encodings]
        if invalid:
            raise ValueError('unexpected encoding parameters for %r backend: '
                             ' %r' % (backend, invalid))
    else:
        for k in list(encoding):
            if k not in valid_encodings:
                del encoding[k]

    return encoding