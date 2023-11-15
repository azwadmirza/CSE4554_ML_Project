def get_pyramid_and_rgb(data, pyramid=None, rgb=None):
    """Check if data is or needs to be a pyramid and make one if needed.

    Parameters
    ----------
    data : array or list
        Data to be checked if pyramid or if needs to be turned into a pyramid.
    pyramid : bool, optional
        Value that can force data to be considered as a pyramid or not,
        otherwise computed.
    rgb : bool, optional
        Value that can force data to be considered as a rgb, otherwise
        computed.

    Returns
    -------
    ndim : int
        Dimensionality of the data.
    rgb : bool
        If data is rgb.
    pyramid : bool
        If data is a pyramid or a pyramid has been generated.
    data_pyramid : list or None
        If None then data is not and does not need to be a pyramid. Otherwise
        is a list of arrays where each array is a level of the pyramid.
    """
    # Determine if data currently is a pyramid
    currently_pyramid = is_pyramid(data)
    if currently_pyramid:
        init_shape = data[0].shape
    else:
        init_shape = data.shape

    # Determine if rgb, and determine dimensionality
    if rgb is False:
        pass
    else:
        # If rgb is True or None then guess if rgb
        # allowed or not, and if allowed set it to be True
        rgb = is_rgb(init_shape)

    if rgb:
        ndim = len(init_shape) - 1
    else:
        ndim = len(init_shape)

    if pyramid is False:
        if currently_pyramid:
            raise ValueError(
                """Non pyramided data was requested, but pyramid
                             data was passed"""
            )
        else:
            data_pyramid = None
    else:
        if currently_pyramid:
            data_pyramid = trim_pyramid(data)
            pyramid = True
        else:
            # Guess if data should be pyramid
            pyr_axes = should_be_pyramid(data.shape)
            if np.any(pyr_axes):
                pyramid = True
                # Set axes to be downsampled to have a factor of 2
                downscale = np.ones(len(data.shape))
                downscale[pyr_axes] = 2
                largest = np.min(np.array(data.shape)[pyr_axes])
                # Determine number of downsample steps needed
                max_layer = np.floor(np.log2(largest) - 9).astype(int)
                data_pyramid = fast_pyramid(
                    data, downscale=downscale, max_layer=max_layer
                )
                data_pyramid = trim_pyramid(data_pyramid)
            else:
                data_pyramid = None
                pyramid = False

    return ndim, rgb, pyramid, data_pyramid