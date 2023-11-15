def local_maxima(image, selem=None):
    """Determine all local maxima of the image.

    The local maxima are defined as connected sets of pixels with equal
    grey level strictly greater than the grey levels of all pixels in direct
    neighborhood of the set.

    For integer typed images, this corresponds to the h-maxima with h=1.
    For float typed images, h is determined as the smallest difference
    between grey levels.

    Parameters
    ----------
    image : ndarray
        The input image for which the maxima are to be calculated.
    selem : ndarray, optional
        The neighborhood expressed as an n-D array of 1's and 0's.
        Default is the ball of radius 1 according to the maximum norm
        (i.e. a 3x3 square for 2D images, a 3x3x3 cube for 3D images, etc.)

    Returns
    -------
    local_max : ndarray
       All local maxima of the image. The result image is a binary image,
       where pixels belonging to local maxima take value 1, the other pixels
       take value 0.

    See also
    --------
    skimage.morphology.extrema.h_minima
    skimage.morphology.extrema.h_maxima
    skimage.morphology.extrema.local_minima

    References
    ----------
    .. [1] Soille, P., "Morphological Image Analysis: Principles and
           Applications" (Chapter 6), 2nd edition (2003), ISBN 3540429883.

    Examples
    --------
    >>> import numpy as np
    >>> from skimage.morphology import extrema

    We create an image (quadratic function with a maximum in the center and
    4 additional constant maxima.
    The heights of the maxima are: 1, 21, 41, 61, 81, 101

    >>> w = 10
    >>> x, y = np.mgrid[0:w,0:w]
    >>> f = 20 - 0.2*((x - w/2)**2 + (y-w/2)**2)
    >>> f[2:4,2:4] = 40; f[2:4,7:9] = 60; f[7:9,2:4] = 80; f[7:9,7:9] = 100
    >>> f = f.astype(np.int)

    We can calculate all local maxima:

    >>> maxima = extrema.local_maxima(f)

    The resulting image will contain all 6 local maxima.
    """
    # find the minimal grey level difference
    h = _find_min_diff(image)
    if h == 0:
        return np.zeros(image.shape, np.uint8)
    if not np.issubdtype(image.dtype, 'half'):
        h = 1
    local_max = h_maxima(image, h, selem=selem)
    return local_max