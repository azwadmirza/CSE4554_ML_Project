def split_channels(
    data: np.ndarray, channel_axis: int, **kwargs,
) -> List[FullLayerData]:
    """Split the data array into separate arrays along an axis.

    Keyword arguments will override any parameters altered or set in this
    function. Colormap, blending, or multiscale are set as follows if not
    overridden by a keyword:
    - colormap : (magenta, green) for 2 channels, (CYMRGB) for more than 2
    - blending : additive
    - multiscale : determined by layers.image._image_utils.guess_multiscale.

    Colormap, blending and multiscale will be set and returned in meta if not in kwargs.
    If any other key is not present in kwargs it will not be returned in the meta
    dictionary of the returned LaterData tuple. For example, if gamma is not in
    kwargs then meta will not have a gamma key.

    Parameters
    ----------
    data : array or list of array
    channel_axis : int
        Axis to split the image along.
    kwargs: dict
        Keyword arguments will override the default image meta keys
        returned in each layer data tuple.

    Returns
    -------
    List of LayerData tuples: [(data: array, meta: Dict, type: str )]
    """

    # Determine if data is a multiscale
    multiscale = kwargs.get('multiscale')
    if not multiscale:
        multiscale, data = guess_multiscale(data)
        kwargs['multiscale'] = multiscale

    n_channels = (data[0] if multiscale else data).shape[channel_axis]

    kwargs['blending'] = kwargs.get('blending') or 'additive'
    kwargs.setdefault('colormap', None)
    # these arguments are *already* iterables in the single-channel case.
    iterable_kwargs = {'scale', 'translate', 'contrast_limits', 'metadata'}

    # turn the kwargs dict into a mapping of {key: iterator}
    # so that we can use {k: next(v) for k, v in kwargs.items()} below
    for key, val in kwargs.items():
        if key == 'colormap' and val is None:
            if n_channels == 1:
                kwargs[key] = iter(['gray'])
            elif n_channels == 2:
                kwargs[key] = iter(MAGENTA_GREEN)
            else:
                kwargs[key] = itertools.cycle(CYMRGB)

        # make sure that iterable_kwargs are a *sequence* of iterables
        # for the multichannel case.  For example: if scale == (1, 2) &
        # n_channels = 3, then scale should == [(1, 2), (1, 2), (1, 2)]
        elif key in iterable_kwargs or (
            key == 'colormap' and isinstance(val, Colormap)
        ):
            kwargs[key] = iter(ensure_sequence_of_iterables(val, n_channels))
        else:
            kwargs[key] = iter(ensure_iterable(val))

    layerdata_list = list()
    for i in range(n_channels):
        if multiscale:
            image = [
                np.take(data[j], i, axis=channel_axis)
                for j in range(len(data))
            ]
        else:
            image = np.take(data, i, axis=channel_axis)
        i_kwargs = {}
        for key, val in kwargs.items():
            try:
                i_kwargs[key] = next(val)
            except StopIteration:
                raise IndexError(
                    "Error adding multichannel image with data shape "
                    f"{data.shape!r}.\nRequested channel_axis "
                    f"({channel_axis}) had length {n_channels}, but "
                    f"the '{key}' argument only provided {i} values. "
                )

        layerdata = (image, i_kwargs, 'image')
        layerdata_list.append(layerdata)

    return layerdata_list