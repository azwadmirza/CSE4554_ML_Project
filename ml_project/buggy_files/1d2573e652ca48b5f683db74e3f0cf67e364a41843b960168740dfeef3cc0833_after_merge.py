def slepian(M, width, sym=True):
    """Return a digital Slepian (DPSS) window.

    Used to maximize the energy concentration in the main lobe.  Also called
    the digital prolate spheroidal sequence (DPSS).

    Parameters
    ----------
    M : int
        Number of points in the output window. If zero or less, an empty
        array is returned.
    width : float
        Bandwidth
    sym : bool, optional
        When True (default), generates a symmetric window, for use in filter
        design.
        When False, generates a periodic window, for use in spectral analysis.

    Returns
    -------
    w : ndarray
        The window, with the maximum value always normalized to 1

    Examples
    --------
    Plot the window and its frequency response:

    >>> from scipy import signal
    >>> from scipy.fftpack import fft, fftshift
    >>> import matplotlib.pyplot as plt

    >>> window = signal.slepian(51, width=0.3)
    >>> plt.plot(window)
    >>> plt.title("Slepian (DPSS) window (BW=0.3)")
    >>> plt.ylabel("Amplitude")
    >>> plt.xlabel("Sample")

    >>> plt.figure()
    >>> A = fft(window, 2048) / (len(window)/2.0)
    >>> freq = np.linspace(-0.5, 0.5, len(A))
    >>> response = 20 * np.log10(np.abs(fftshift(A / abs(A).max())))
    >>> plt.plot(freq, response)
    >>> plt.axis([-0.5, 0.5, -120, 0])
    >>> plt.title("Frequency response of the Slepian window (BW=0.3)")
    >>> plt.ylabel("Normalized magnitude [dB]")
    >>> plt.xlabel("Normalized frequency [cycles per sample]")

    """
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1, 'd')
    odd = M % 2
    if not sym and not odd:
        M = M + 1

    # our width is the full bandwidth
    width = width / 2
    # to match the old version 
    width = width / 2
    m = np.arange(M, dtype='d')
    H = np.zeros((2, M))
    H[0, 1:] = m[1:] * (M - m[1:]) / 2
    H[1, :] = ((M - 1 - 2 * m) / 2)**2 * np.cos(2 * np.pi * width)

    _, win = linalg.eig_banded(H, select='i', select_range=(M-1, M-1))
    win = win.ravel() / win.max()

    if not sym and not odd:
        win = win[:-1]
    return win