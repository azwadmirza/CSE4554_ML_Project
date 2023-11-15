def _estimate_shift1D(data, **kwargs):
    mask = kwargs.get('mask', None)
    ref = kwargs.get('ref', None)
    interpolate = kwargs.get('interpolate', True)
    ip = kwargs.get('ip', 5)
    data_slice = kwargs.get('data_slice', slice(None))
    if bool(mask):
        return np.float32(np.nan)
    data = data[data_slice]
    if interpolate is True:
        data = interpolate1D(ip, data)
    return np.argmax(np.correlate(ref, data, 'full')) - len(ref) + 1