def translate_xy(
    image: TensorLike, translate_to: TensorLike, replace: int
) -> TensorLike:
    """Translates image in X or Y dimension.

    Args:
        image: A 3D image `Tensor`.
        translate_to: A 1D `Tensor` to translate [x, y]
        replace: A one or three value 1D `Tensor` to fill empty pixels.
    Returns:
        Translated image along X or Y axis, with space outside image
            filled with replace.
    Raises:
        ValueError: if axis is neither 0 nor 1.
    """
    image = tf.convert_to_tensor(image)
    image = wrap(image)
    trans = tf.convert_to_tensor(translate_to)
    image = translate(image, [trans[0], trans[1]])
    return unwrap(image, replace)