def qimage_from_array(arr: np.ndarray) -> QImage:
    """
    Create and return an QImage from a (N, M, C) uint8 array where C is 3 for
    RGB and 4 for RGBA channels.

    Parameters
    ----------
    arr: (N, M C) uint8 array

    Returns
    -------
    image: QImage
        An QImage with size (M, N) in ARGB32 format format depending on `C`.
    """
    h, w, c = arr.shape
    if c == 4:
        format = QImage.Format_ARGB32
    elif c == 3:
        format = QImage.Format_RGB32
    else:
        raise ValueError(f"Wrong number of channels (need 3 or 4, got {c}")
    channels = arr.transpose((2, 0, 1))
    img = QImage(w, h, QImage.Format_ARGB32)
    img.fill(Qt.white)
    if img.size().isEmpty():
        return img
    buffer = img.bits().asarray(w * h * 4)
    view = np.frombuffer(buffer, np.uint32).reshape((h, w))
    if format == QImage.Format_ARGB32:
        view[:, :] = qrgba(*channels)
    elif format == QImage.Format_RGB32:
        view[:, :] = qrgb(*channels)
    return img