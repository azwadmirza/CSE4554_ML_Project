    def add_image(
        self,
        data=None,
        *,
        channel_axis=None,
        rgb=None,
        colormap=None,
        contrast_limits=None,
        gamma=1,
        interpolation='nearest',
        rendering='mip',
        iso_threshold=0.5,
        attenuation=0.5,
        name=None,
        metadata=None,
        scale=None,
        translate=None,
        opacity=1,
        blending=None,
        visible=True,
        multiscale=None,
    ) -> Union[layers.Image, List[layers.Image]]:
        """Add an image layer to the layers list.

        Parameters
        ----------
        data : array or list of array
            Image data. Can be N dimensional. If the last dimension has length
            3 or 4 can be interpreted as RGB or RGBA if rgb is `True`. If a
            list and arrays are decreasing in shape then the data is treated as
            a multiscale image.
        channel_axis : int, optional
            Axis to expand image along.  If provided, each channel in the data
            will be added as an individual image layer.  In channel_axis mode,
            all other parameters MAY be provided as lists, and the Nth value
            will be applied to the Nth channel in the data.  If a single value
            is provided, it will be broadcast to all Layers.
        rgb : bool or list
            Whether the image is rgb RGB or RGBA. If not specified by user and
            the last dimension of the data has length 3 or 4 it will be set as
            `True`. If `False` the image is interpreted as a luminance image.
            If a list then must be same length as the axis that is being
            expanded as channels.
        colormap : str, vispy.Color.Colormap, tuple, dict, list
            Colormaps to use for luminance images. If a string must be the name
            of a supported colormap from vispy or matplotlib. If a tuple the
            first value must be a string to assign as a name to a colormap and
            the second item must be a Colormap. If a dict the key must be a
            string to assign as a name to a colormap and the value must be a
            Colormap. If a list then must be same length as the axis that is
            being expanded as channels, and each colormap is applied to each
            new image layer.
        contrast_limits : list (2,)
            Color limits to be used for determining the colormap bounds for
            luminance images. If not passed is calculated as the min and max of
            the image. If list of lists then must be same length as the axis
            that is being expanded and then each colormap is applied to each
            image.
        gamma : list, float
            Gamma correction for determining colormap linearity. Defaults to 1.
            If a list then must be same length as the axis that is being
            expanded as channels.
        interpolation : str or list
            Interpolation mode used by vispy. Must be one of our supported
            modes. If a list then must be same length as the axis that is being
            expanded as channels.
        rendering : str or list
            Rendering mode used by vispy. Must be one of our supported
            modes. If a list then must be same length as the axis that is being
            expanded as channels.
        iso_threshold : float or list
            Threshold for isosurface. If a list then must be same length as the
            axis that is being expanded as channels.
        attenuation : float or list
            Attenuation rate for attenuated maximum intensity projection. If a
            list then must be same length as the axis that is being expanded as
            channels.
        name : str or list of str
            Name of the layer.  If a list then must be same length as the axis
            that is being expanded as channels.
        metadata : dict or list of dict
            Layer metadata. If a list then must be a list of dicts with the
            same length as the axis that is being expanded as channels.
        scale : tuple of float or list
            Scale factors for the layer. If a list then must be a list of
            tuples of float with the same length as the axis that is being
            expanded as channels.
        translate : tuple of float or list
            Translation values for the layer. If a list then must be a list of
            tuples of float with the same length as the axis that is being
            expanded as channels.
        opacity : float or list
            Opacity of the layer visual, between 0.0 and 1.0.  If a list then
            must be same length as the axis that is being expanded as channels.
        blending : str or list
            One of a list of preset blending modes that determines how RGB and
            alpha values of the layer visual get mixed. Allowed values are
            {'opaque', 'translucent', and 'additive'}. If a list then
            must be same length as the axis that is being expanded as channels.
        visible : bool or list of bool
            Whether the layer visual is currently being displayed.
            If a list then must be same length as the axis that is
            being expanded as channels.
        multiscale : bool
            Whether the data is a multiscale image or not. Multiscale data is
            represented by a list of array like image data. If not specified by
            the user and if the data is a list of arrays that decrease in shape
            then it will be taken to be multiscale. The first image in the list
            should be the largest.

        Returns
        -------
        layer : :class:`napari.layers.Image` or list
            The newly-created image layer or list of image layers.
        """

        if colormap is not None:
            # standardize colormap argument(s) to strings, and make sure they
            # are in AVAILABLE_COLORMAPS.  This will raise one of many various
            # errors if the colormap argument is invalid.  See
            # ensure_colormap_tuple for details
            if isinstance(colormap, list):
                colormap = [ensure_colormap_tuple(c)[0] for c in colormap]
            else:
                colormap, _ = ensure_colormap_tuple(colormap)

        # doing this here for IDE/console autocompletion in add_image function.
        kwargs = {
            'rgb': rgb,
            'colormap': colormap,
            'contrast_limits': contrast_limits,
            'gamma': gamma,
            'interpolation': interpolation,
            'rendering': rendering,
            'iso_threshold': iso_threshold,
            'attenuation': attenuation,
            'name': name,
            'metadata': metadata,
            'scale': scale,
            'translate': translate,
            'opacity': opacity,
            'blending': blending,
            'visible': visible,
            'multiscale': multiscale,
        }

        # these arguments are *already* iterables in the single-channel case.
        iterable_kwargs = {'scale', 'translate', 'contrast_limits', 'metadata'}

        if channel_axis is None:
            kwargs['colormap'] = kwargs['colormap'] or 'gray'
            kwargs['blending'] = kwargs['blending'] or 'translucent'
            # Helpful message if someone tries to add mulit-channel kwargs,
            # but forget the channel_axis arg
            for k, v in kwargs.items():
                if k not in iterable_kwargs and is_sequence(v):
                    raise TypeError(
                        f"Received sequence for argument '{k}', "
                        "did you mean to specify a 'channel_axis'? "
                    )

            return self.add_layer(layers.Image(data, **kwargs))
        else:
            # Determine if data is a multiscale
            if multiscale is None:
                multiscale = guess_multiscale(data)
            n_channels = (data[0] if multiscale else data).shape[channel_axis]
            kwargs['blending'] = kwargs['blending'] or 'additive'

            # turn the kwargs dict into a mapping of {key: iterator}
            # so that we can use {k: next(v) for k, v in kwargs.items()} below
            for key, val in kwargs.items():
                if key == 'colormap' and val is None:
                    if n_channels == 1:
                        kwargs[key] = iter(['gray'])
                    elif n_channels == 2:
                        kwargs[key] = iter(colormaps.MAGENTA_GREEN)
                    else:
                        kwargs[key] = itertools.cycle(colormaps.CYMRGB)

                # make sure that iterable_kwargs are a *sequence* of iterables
                # for the multichannel case.  For example: if scale == (1, 2) &
                # n_channels = 3, then scale should == [(1, 2), (1, 2), (1, 2)]
                elif key in iterable_kwargs:
                    kwargs[key] = iter(
                        ensure_sequence_of_iterables(val, n_channels)
                    )
                else:
                    kwargs[key] = iter(ensure_iterable(val))

            layer_list = []
            for i in range(n_channels):
                if multiscale:
                    image = [
                        np.take(data[j], i, axis=channel_axis)
                        for j in range(len(data))
                    ]
                else:
                    image = np.take(data, i, axis=channel_axis)
                i_kwargs = {k: next(v) for k, v in kwargs.items()}
                layer = self.add_layer(layers.Image(image, **i_kwargs))
                layer_list.append(layer)
            return layer_list