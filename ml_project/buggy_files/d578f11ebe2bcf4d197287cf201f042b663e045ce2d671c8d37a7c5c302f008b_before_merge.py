def get_enhanced_image(dataset, ppp_config_dir=None, enhance=None, enhancement_config_file=None,
                       overlay=None, decorate=None, fill_value=None):
    """Get an enhanced version of `dataset` as an :class:`~trollimage.xrimage.XRImage` instance.

    Args:
        dataset (xarray.DataArray): Data to be enhanced and converted to an image.
        ppp_config_dir (str): Root configuration directory.
        enhance (bool or Enhancer): Whether to automatically enhance
            data to be more visually useful and to fit inside the file
            format being saved to. By default this will default to using
            the enhancement configuration files found using the default
            :class:`~satpy.writers.Enhancer` class. This can be set to
            `False` so that no enhancments are performed. This can also
            be an instance of the :class:`~satpy.writers.Enhancer` class
            if further custom enhancement is needed.
        enhancement_config_file (str): Deprecated.
        overlay (dict): Options for image overlays. See :func:`add_overlay`
            for available options.
        decorate (dict): Options for decorating the image. See
            :func:`add_decorate` for available options.
        fill_value (int or float): Value to use when pixels are masked or
            invalid. Default of `None` means to create an alpha channel.
            See :meth:`~trollimage.xrimage.XRImage.finalize` for more
            details. Only used when adding overlays or decorations. Otherwise
            it is up to the caller to "finalize" the image before using it
            except if calling ``img.show()`` or providing the image to
            a writer as these will finalize the image.

    .. versionchanged:: 0.10

        Deprecated `enhancement_config_file` and 'enhancer' in favor of
        `enhance`. Pass an instance of the `Enhancer` class to `enhance`
        instead.

    """
    if ppp_config_dir is None:
        ppp_config_dir = get_environ_config_dir()

    if enhancement_config_file is not None:
        warnings.warn("'enhancement_config_file' has been deprecated. Pass an instance of the "
                      "'Enhancer' class to the 'enhance' keyword argument instead.", DeprecationWarning)

    if enhance is False:
        # no enhancement
        enhancer = None
    elif enhance is None or enhance is True:
        # default enhancement
        enhancer = Enhancer(ppp_config_dir, enhancement_config_file)
    else:
        # custom enhancer
        enhancer = enhance

    # Create an image for enhancement
    img = to_image(dataset)

    if enhancer is None or enhancer.enhancement_tree is None:
        LOG.debug("No enhancement being applied to dataset")
    else:
        if dataset.attrs.get("sensor", None):
            enhancer.add_sensor_enhancements(dataset.attrs["sensor"])

        enhancer.apply(img, **dataset.attrs)

    if overlay is not None:
        add_overlay(img, dataset.attrs['area'], fill_value=fill_value, **overlay)

    if decorate is not None:
        add_decorate(img, fill_value=fill_value, **decorate)

    return img