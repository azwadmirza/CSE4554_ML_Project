def blob_dog(image, min_sigma=1, max_sigma=50, sigma_ratio=1.6, threshold=2.0,
             overlap=.5,):
    """Finds blobs in the given grayscale image.

    Blobs are found using the Difference of Gaussian (DoG) method [1]_.
    For each blob found, the method returns its coordinates and the standard
    deviation of the Gaussian kernel that detected the blob.

    Parameters
    ----------
    image : ndarray
        Input grayscale image, blobs are assumed to be light on dark
        background (white on black).
    min_sigma : float, optional
        The minimum standard deviation for Gaussian Kernel. Keep this low to
        detect smaller blobs.
    max_sigma : float, optional
        The maximum standard deviation for Gaussian Kernel. Keep this high to
        detect larger blobs.
    sigma_ratio : float, optional
        The ratio between the standard deviation of Gaussian Kernels used for
        computing the Difference of Gaussians
    threshold : float, optional.
        The absolute lower bound for scale space maxima. Local maxima smaller
        than thresh are ignored. Reduce this to detect blobs with less
        intensities.
    overlap : float, optional
        A value between 0 and 1. If the area of two blobs overlaps by a
        fraction greater than `threshold`, the smaller blob is eliminated.

    Returns
    -------
    A : (n, 3) ndarray
        A 2d array with each row representing 3 values, ``(y,x,sigma)``
        where ``(y,x)`` are coordinates of the blob and ``sigma`` is the
        standard deviation of the Gaussian kernel which detected the blob.

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Blob_detection#The_difference_of_Gaussians_approach

    Examples
    --------
    >>> from skimage import data, feature
    >>> feature.blob_dog(data.coins(), threshold=.5, max_sigma=40)
    array([[  45.      ,  336.      ,   16.777216],
           [  52.      ,  155.      ,   16.777216],
           [  52.      ,  216.      ,   16.777216],
           [  54.      ,   42.      ,   16.777216],
           [  54.      ,  276.      ,   10.48576 ],
           [  58.      ,  100.      ,   10.48576 ],
           [ 120.      ,  272.      ,   16.777216],
           [ 124.      ,  337.      ,   10.48576 ],
           [ 125.      ,   45.      ,   16.777216],
           [ 125.      ,  208.      ,   10.48576 ],
           [ 127.      ,  102.      ,   10.48576 ],
           [ 128.      ,  154.      ,   10.48576 ],
           [ 185.      ,  347.      ,   16.777216],
           [ 193.      ,  213.      ,   16.777216],
           [ 194.      ,  277.      ,   16.777216],
           [ 195.      ,  102.      ,   16.777216],
           [ 196.      ,   43.      ,   10.48576 ],
           [ 198.      ,  155.      ,   10.48576 ],
           [ 260.      ,   46.      ,   16.777216],
           [ 261.      ,  173.      ,   16.777216],
           [ 263.      ,  245.      ,   16.777216],
           [ 263.      ,  302.      ,   16.777216],
           [ 267.      ,  115.      ,   10.48576 ],
           [ 267.      ,  359.      ,   16.777216]])

    Notes
    -----
    The radius of each blob is approximately :math:`\sqrt{2}sigma`.
    """
    assert_nD(image, 2)

    image = img_as_float(image)

    # k such that min_sigma*(sigma_ratio**k) > max_sigma
    k = int(log(float(max_sigma) / min_sigma, sigma_ratio)) + 1

    # a geometric progression of standard deviations for gaussian kernels
    sigma_list = np.array([min_sigma * (sigma_ratio ** i)
                           for i in range(k + 1)])

    gaussian_images = [gaussian_filter(image, s) for s in sigma_list]

    # computing difference between two successive Gaussian blurred images
    # multiplying with standard deviation provides scale invariance
    dog_images = [(gaussian_images[i] - gaussian_images[i + 1])
                  * sigma_list[i] for i in range(k)]
    image_cube = np.dstack(dog_images)

    # local_maxima = get_local_maxima(image_cube, threshold)
    local_maxima = peak_local_max(image_cube, threshold_abs=threshold,
                                  footprint=np.ones((3, 3, 3)),
                                  threshold_rel=0.0,
                                  exclude_border=False)
    # Convert local_maxima to float64
    lm = local_maxima.astype(np.float64)
    # Convert the last index to its corresponding scale value
    lm[:, 2] = sigma_list[local_maxima[:, 2]]
    local_maxima = lm
    return _prune_blobs(local_maxima, overlap)