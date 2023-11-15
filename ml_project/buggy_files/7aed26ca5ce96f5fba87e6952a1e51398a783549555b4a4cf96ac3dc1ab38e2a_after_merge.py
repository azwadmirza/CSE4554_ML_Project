def view_image(
    data=None,
    *,
    channel_axis=None,
    rgb=None,
    is_pyramid=None,
    colormap=None,
    contrast_limits=None,
    gamma=1,
    interpolation='nearest',
    rendering='mip',
    name=None,
    metadata=None,
    scale=None,
    translate=None,
    opacity=1,
    blending=None,
    visible=True,
    path=None,
    title='napari',
    ndisplay=2,
    order=None,
    axis_labels=None,
):
    """Create a viewer and add an image layer.

    Parameters
    ----------
    data : array or list of array
        Image data. Can be N dimensional. If the last dimension has length
        3 or 4 can be interpreted as RGB or RGBA if rgb is `True`. If a
        list and arrays are decreasing in shape then the data is treated as
        an image pyramid.
    channel_axis : int, optional
        Axis to expand image along.
    rgb : bool
        Whether the image is rgb RGB or RGBA. If not specified by user and
        the last dimension of the data has length 3 or 4 it will be set as
        `True`. If `False` the image is interpreted as a luminance image.
    is_pyramid : bool
        Whether the data is an image pyramid or not. Pyramid data is
        represented by a list of array like image data. If not specified by
        the user and if the data is a list of arrays that decrease in shape
        then it will be taken to be a pyramid. The first image in the list
        should be the largest.
    colormap : str, vispy.Color.Colormap, tuple, dict, list
        Colormaps to use for luminance images. If a string must be the name
        of a supported colormap from vispy or matplotlib. If a tuple the
        first value must be a string to assign as a name to a colormap and
        the second item must be a Colormap. If a dict the key must be a
        string to assign as a name to a colormap and the value must be a
        Colormap. If a list then must be same length as the axis that is
        being expanded as channels, and each colormap is applied to each new
        image layer.
    contrast_limits : list (2,)
        Color limits to be used for determining the colormap bounds for
        luminance images. If not passed is calculated as the min and max of
        the image. If list of lists then must be same length as the axis
        that is being expanded and then each colormap is applied to each
        image.
    gamma : list, float
        Gamma correction for determining colormap linearity. Defaults to 1.
        If a list then must be same length as the axis that is being expanded
        and then each entry in the list is applied to each image.
    interpolation : str
        Interpolation mode used by vispy. Must be one of our supported
        modes.
    name : str
        Name of the layer.
    metadata : dict
        Layer metadata.
    scale : tuple of float
        Scale factors for the layer.
    translate : tuple of float
        Translation values for the layer.
    opacity : float
        Opacity of the layer visual, between 0.0 and 1.0.
    blending : str
        One of a list of preset blending modes that determines how RGB and
        alpha values of the layer visual get mixed. Allowed values are
        {'opaque', 'translucent', and 'additive'}.
    visible : bool
        Whether the layer visual is currently being displayed.
    path : str or list of str
        Path or list of paths to image data.
    title : string
        The title of the viewer window.
    ndisplay : {2, 3}
        Number of displayed dimensions.
    order : tuple of int
        Order in which dimensions are displayed where the last two or last
        three dimensions correspond to row x column or plane x row x column if
        ndisplay is 2 or 3.
    axis_labels : list of str
        Dimension names.

    Returns
    -------
    viewer : :class:`napari.Viewer`
        The newly-created viewer.
    """
    viewer = Viewer(
        title=title, ndisplay=ndisplay, order=order, axis_labels=axis_labels
    )
    viewer.add_image(
        data=data,
        channel_axis=channel_axis,
        rgb=rgb,
        is_pyramid=is_pyramid,
        colormap=colormap,
        contrast_limits=contrast_limits,
        gamma=gamma,
        interpolation=interpolation,
        rendering=rendering,
        name=name,
        metadata=metadata,
        scale=scale,
        translate=translate,
        opacity=opacity,
        blending=blending,
        visible=visible,
        path=path,
    )
    return viewer