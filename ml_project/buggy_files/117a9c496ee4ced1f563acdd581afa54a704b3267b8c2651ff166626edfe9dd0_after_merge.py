def shear_y(image: TensorLike, level: float, replace: TensorLike) -> TensorLike:
    """Perform shear operation on an image (y-axis).

    Args:
        image: A 3D image `Tensor`.
        level: A float denoting shear element along x-axis
        replace: A one or three value 1D tensor to fill empty pixels.
    Returns:
        Transformed image along X or Y axis, with space outside image
        filled with replace.
    """
    # Shear parallel to y axis is a projective transform
    # with a matrix form of:
    # [1  0
    #  level  1].
    image = transform(wrap(image), [1.0, 0.0, 0.0, level, 1.0, 0.0, 0.0, 0.0])
    return unwrap(image, replace)