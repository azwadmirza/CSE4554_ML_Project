def _shift1D(data, **kwargs):
    shift = kwargs.get('shift', 0.)
    original_axis = kwargs.get('original_axis', None)
    fill_value = kwargs.get('fill_value', np.nan)
    kind = kwargs.get('kind', 'linear')
    offset = kwargs.get('offset', 0.)
    scale = kwargs.get('scale', 1.)
    size = kwargs.get('size', 2)
    if np.isnan(shift) or shift == 0:
        return data
    axis = np.linspace(offset, offset + scale * (size - 1), size)

    si = sp.interpolate.interp1d(original_axis,
                                 data,
                                 bounds_error=False,
                                 fill_value=fill_value,
                                 kind=kind)
    offset = float(offset - shift)
    axis = np.linspace(offset, offset + scale * (size - 1), size)
    return si(axis)