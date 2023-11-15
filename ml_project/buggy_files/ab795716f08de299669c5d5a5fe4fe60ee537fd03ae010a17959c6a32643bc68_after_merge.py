def _get_and_verify_data_sizes(data, sfreq, n_signals=None, n_times=None,
                               times=None):
    """Get and/or verify the data sizes and time scales."""
    if not isinstance(data, (list, tuple)):
        raise ValueError('data has to be a list or tuple')
    n_signals_tot = 0
    for this_data in data:
        this_n_signals, this_n_times = this_data.shape
        if n_times is not None:
            if this_n_times != n_times:
                raise ValueError('all input time series must have the same '
                                 'number of time points')
        else:
            n_times = this_n_times
        n_signals_tot += this_n_signals

        if hasattr(this_data, 'times'):
            assert isinstance(this_data, _BaseSourceEstimate)
            this_times = this_data.times
            if times is not None:
                if np.any(times != this_times):
                    warn('time scales of input time series do not match')
            else:
                times = this_times
        elif times is None:
            times = _arange_div(n_times, sfreq)

    if n_signals is not None:
        if n_signals != n_signals_tot:
            raise ValueError('the number of time series has to be the same in '
                             'each epoch')
    n_signals = n_signals_tot

    return n_signals, n_times, times