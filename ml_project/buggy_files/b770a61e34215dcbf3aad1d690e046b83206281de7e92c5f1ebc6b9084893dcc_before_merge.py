def unwrap(image, replace):
    """Unwraps an image produced by wrap.

    Where there is a 0 in the last channel for every spatial position,
    the rest of the three channels in that spatial dimension are grayed
    (set to 128).  Operations like translate and shear on a wrapped
    Tensor will leave 0s in empty locations.  Some transformations look
    at the intensity of values to do preprocessing, and we want these
    empty pixels to assume the 'average' value, rather than pure black.


    Args:
        image: A 3D image `Tensor` with 4 channels.
        replace: A one or three value 1D `Tensor` to fill empty pixels.

    Returns:
        image: A 3D image `Tensor` with 3 channels.
    """
    image_shape = tf.shape(image)
    # Flatten the spatial dimensions.
    flattened_image = tf.reshape(image, [-1, image_shape[2]])

    # Find all pixels where the last channel is zero.
    alpha_channel = flattened_image[:, 3]

    replace = tf.constant(replace, tf.uint8)
    if tf.rank(replace) == 0:
        replace = tf.expand_dims(replace, 0)
        replace = tf.concat([replace, replace, replace], 0)
    replace = tf.concat([replace, tf.ones([1], dtype=image.dtype)], 0)

    # Where they are zero, fill them in with 'replace'.
    cond = tf.equal(alpha_channel, 1)
    cond = tf.expand_dims(cond, 1)
    cond = tf.concat([cond, cond, cond, cond], 1)
    flattened_image = tf.where(cond, flattened_image, replace)

    image = tf.reshape(flattened_image, image_shape)
    image = tf.slice(image, [0, 0, 0], [image_shape[0], image_shape[1], 3])
    return image