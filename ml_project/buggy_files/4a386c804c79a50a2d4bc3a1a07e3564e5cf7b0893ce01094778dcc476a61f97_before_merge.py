def _find_min_diff(image):
    """
    Find the minimal difference of grey levels inside the image.
    """
    img_vec = np.unique(image.flatten())
    min_diff = np.min(img_vec[1:] - img_vec[:-1])
    return min_diff