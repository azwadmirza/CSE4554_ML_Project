def imread(uri, grayscale=False, expand_dims=True, rootpath=None, **kwargs):
    """

    Args:
        uri: {str, pathlib.Path, bytes, file}
        The resource to load the image from, e.g. a filename, pathlib.Path,
        http address or file object, see the docs for more info.
        grayscale:
        expand_dims:
        rootpath:

    Returns:

    """
    if rootpath is not None:
        uri = (
            uri if uri.startswith(rootpath) else os.path.join(rootpath, uri)
        )

    if JPEG4PY_ENABLED and uri.endswith(("jpg", "JPG", "jpeg", "JPEG")):
        img = jpeg.JPEG(uri).decode()
    else:
        img = imageio.imread(uri, **kwargs)
    if grayscale:
        img = rgb2gray(img)

    if expand_dims and len(img.shape) < 3:  # grayscale
        img = np.expand_dims(img, -1)

    return img