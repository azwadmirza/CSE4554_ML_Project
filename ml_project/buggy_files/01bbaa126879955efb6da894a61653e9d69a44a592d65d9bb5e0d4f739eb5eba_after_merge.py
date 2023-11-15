def hold_to_lock_aspect_ratio(layer):
    """Hold to lock aspect ratio when resizing a shape."""
    # on key press
    layer._fixed_aspect = True
    box = layer._selected_box
    if box is not None:
        size = box[Box.BOTTOM_RIGHT] - box[Box.TOP_LEFT]
        if not np.any(size == np.zeros(2)):
            layer._aspect_ratio = abs(size[1] / size[0])
        else:
            layer._aspect_ratio = 1
    else:
        layer._aspect_ratio = 1
    if layer._is_moving:
        layer._move([layer.coordinates[i] for i in layer.dims.displayed])

    yield

    # on key release
    layer._fixed_aspect = False
    if layer._is_moving:
        layer._move([layer.coordinates[i] for i in layer.dims.displayed])