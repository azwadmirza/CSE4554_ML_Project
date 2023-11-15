def qimage_indexed_from_array(
        arr: np.ndarray, colortable: Sequence[Sequence[int]]
) -> QImage:
    arr = np.asarray(arr, dtype=np.uint8)
    h, w = arr.shape
    colortable = np.asarray(colortable, dtype=np.uint8)
    ncolors, nchannels = colortable.shape
    img = QImage(w, h, QImage.Format_Indexed8)
    img.setColorCount(ncolors)
    if nchannels == 4:
        qrgb_ = qrgba
    elif nchannels == 3:
        qrgb_ = qrgb
    else:
        raise ValueError

    for i, c in enumerate(colortable):
        img.setColor(i, qrgb_(*c))

    buffer = img.bits().asarray(w * h)
    view = np.frombuffer(buffer, np.uint8).reshape((h, w))
    view[:, :] = arr
    return img