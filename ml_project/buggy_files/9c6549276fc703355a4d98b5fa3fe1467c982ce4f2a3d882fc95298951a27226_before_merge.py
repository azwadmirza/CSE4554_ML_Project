def cutout(
    images: TensorLike,
    mask_size: TensorLike,
    offset: TensorLike = (0, 0),
    constant_values: Number = 0,
    data_format: str = "channels_last",
) -> tf.Tensor:
    """Apply cutout (https://arxiv.org/abs/1708.04552) to images.

    This operation applies a (mask_height x mask_width) mask of zeros to
    a location within `img` specified by the offset. The pixel values filled in will be of the
    value `replace`. The located where the mask will be applied is randomly
    chosen uniformly over the whole images.

    Args:
      images: A tensor of shape (batch_size, height, width, channels)
        (NHWC), (batch_size, channels, height, width)(NCHW).
      mask_size: Specifies how big the zero mask that will be generated is that
        is applied to the images. The mask will be of size
        (mask_height x mask_width). Note: mask_size should be divisible by 2.
      offset: A tuple of (height, width) or (batch_size, 2)
      constant_values: What pixel value to fill in the images in the area that has
        the cutout mask applied to it.
      data_format: A string, one of `channels_last` (default) or `channels_first`.
        The ordering of the dimensions in the inputs.
        `channels_last` corresponds to inputs with shape
        `(batch_size, ..., channels)` while `channels_first` corresponds to
        inputs with shape `(batch_size, channels, ...)`.
    Returns:
      An image Tensor.
    Raises:
      InvalidArgumentError: if mask_size can't be divisible by 2.
    """
    with tf.name_scope("cutout"):
        offset = tf.convert_to_tensor(offset)
        mask_size, data_format, image_height, image_width = _norm_params(
            images, mask_size, data_format
        )
        mask_size = mask_size // 2

        if tf.rank(offset) == 1:
            offset = tf.expand_dims(offset, 0)
        cutout_center_heights = offset[:, 0]
        cutout_center_widths = offset[:, 1]

        lower_pads = tf.maximum(0, cutout_center_heights - mask_size[0])
        upper_pads = tf.maximum(0, image_height - cutout_center_heights - mask_size[0])
        left_pads = tf.maximum(0, cutout_center_widths - mask_size[1])
        right_pads = tf.maximum(0, image_width - cutout_center_widths - mask_size[1])

        cutout_shape = tf.transpose(
            [
                image_height - (lower_pads + upper_pads),
                image_width - (left_pads + right_pads),
            ],
            [1, 0],
        )
        masks = tf.TensorArray(images.dtype, 0, dynamic_size=True)
        for i in tf.range(tf.shape(cutout_shape)[0]):
            padding_dims = [
                [lower_pads[i], upper_pads[i]],
                [left_pads[i], right_pads[i]],
            ]
            mask = tf.pad(
                tf.zeros(cutout_shape[i], dtype=images.dtype),
                padding_dims,
                constant_values=1,
            )
            masks = masks.write(i, mask)

        if data_format == "channels_last":
            mask_4d = tf.expand_dims(masks.stack(), -1)
            mask = tf.tile(mask_4d, [1, 1, 1, tf.shape(images)[-1]])
        else:
            mask_4d = tf.expand_dims(masks.stack(), 1)
            mask = tf.tile(mask_4d, [1, tf.shape(images)[1], 1, 1])
        images = tf.where(
            mask == 0,
            tf.ones_like(images, dtype=images.dtype) * constant_values,
            images,
        )
        return images