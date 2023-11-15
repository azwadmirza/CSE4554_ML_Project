def check_COLA(window, nperseg, noverlap, tol=1e-10):
    r"""
    Check whether the Constant OverLap Add (COLA) constraint is met

    Parameters
    ----------
    window : str or tuple or array_like
        Desired window to use. If `window` is a string or tuple, it is
        passed to `get_window` to generate the window values, which are
        DFT-even by default. See `get_window` for a list of windows and
        required parameters. If `window` is array_like it will be used
        directly as the window and its length must be nperseg.
    nperseg : int
        Length of each segment.
    noverlap : int
        Number of points to overlap between segments.
    tol : float, optional
        The allowed variance of a bin's weighted sum from the median bin
        sum.

    Returns
    -------
    verdict : bool
        `True` if chosen combination satisfies COLA within `tol`,
        `False` otherwise

    See Also
    --------
    stft: Short Time Fourier Transform
    istft: Inverse Short Time Fourier Transform

    Notes
    -----
    In order to enable inversion of an STFT via the inverse STFT in
    `istft`, the signal windowing must obey the constraint of "Constant
    OverLap Add" (COLA). This ensures that every point in the input data
    is equally weighted, thereby avoiding aliasing and allowing full
    reconstruction.

    Some examples of windows that satisfy COLA:
        - Rectangular window at overlap of 0, 1/2, 2/3, 3/4, ...
        - Bartlett window at overlap of 1/2, 3/4, 5/6, ...
        - Hann window at 1/2, 2/3, 3/4, ...
        - Any Blackman family window at 2/3 overlap
        - Any window with ``noverlap = nperseg-1``

    A very comprehensive list of other windows may be found in [2]_,
    wherein the COLA condition is satisfied when the "Amplitude
    Flatness" is unity.

    .. versionadded:: 0.19.0

    References
    ----------
    .. [1] Julius O. Smith III, "Spectral Audio Signal Processing", W3K
           Publishing, 2011,ISBN 978-0-9745607-3-1.
    .. [2] G. Heinzel, A. Ruediger and R. Schilling, "Spectrum and
           spectral density estimation by the Discrete Fourier transform
           (DFT), including a comprehensive list of window functions and
           some new at-top windows", 2002,
           http://hdl.handle.net/11858/00-001M-0000-0013-557A-5

    Examples
    --------
    >>> from scipy import signal

    Confirm COLA condition for rectangular window of 75% (3/4) overlap:

    >>> signal.check_COLA(signal.boxcar(100), 100, 75)
    True

    COLA is not true for 25% (1/4) overlap, though:

    >>> signal.check_COLA(signal.boxcar(100), 100, 25)
    False

    "Symmetrical" Hann window (for filter design) is not COLA:

    >>> signal.check_COLA(signal.hann(120, sym=True), 120, 60)
    False

    "Periodic" or "DFT-even" Hann window (for FFT analysis) is COLA for
    overlap of 1/2, 2/3, 3/4, etc.:

    >>> signal.check_COLA(signal.hann(120, sym=False), 120, 60)
    True

    >>> signal.check_COLA(signal.hann(120, sym=False), 120, 80)
    True

    >>> signal.check_COLA(signal.hann(120, sym=False), 120, 90)
    True

    """

    nperseg = int(nperseg)

    if nperseg < 1:
        raise ValueError('nperseg must be a positive integer')

    if noverlap >= nperseg:
        raise ValueError('noverlap must be less than nperseg.')
    noverlap = int(noverlap)

    if isinstance(window, string_types) or type(window) is tuple:
        win = get_window(window, nperseg)
    else:
        win = np.asarray(window)
        if len(win.shape) != 1:
            raise ValueError('window must be 1-D')
        if win.shape[0] != nperseg:
            raise ValueError('window must have length of nperseg')

    step = nperseg - noverlap
    binsums = sum(win[ii*step:(ii+1)*step] for ii in range(nperseg//step))

    if nperseg % step != 0:
        binsums[:nperseg % step] += win[-(nperseg % step):]

    deviation = binsums - np.median(binsums)
    return np.max(np.abs(deviation)) < tol