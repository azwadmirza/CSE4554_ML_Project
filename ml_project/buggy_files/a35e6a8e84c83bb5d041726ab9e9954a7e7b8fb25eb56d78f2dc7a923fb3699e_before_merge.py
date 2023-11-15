    def add_image(
        self,
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
    ):
        """Add an image layer to the layers list.

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
            expanded and then each entry in the list is applied to each image.
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
            Path or list of paths to image data. Paths can be passed as strings
            or `pathlib.Path` instances.

        Returns
        -------
        layer : :class:`napari.layers.Image` or list
            The newly-created image layer or list of image layers.
        """
        if data is None and path is None:
            raise ValueError("One of either data or path must be provided")
        elif data is not None and path is not None:
            raise ValueError("Only one of data or path can be provided")
        elif data is None:
            data = io.magic_imread(path)

        if channel_axis is None:
            if colormap is None:
                colormap = 'gray'
            if blending is None:
                blending = 'translucent'
            layer = layers.Image(
                data,
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
            )
            self.add_layer(layer)
            return layer
        else:
            if is_pyramid:
                n_channels = data[0].shape[channel_axis]
            else:
                n_channels = data.shape[channel_axis]

            name = ensure_iterable(name)

            if blending is None:
                blending = 'additive'

            if colormap is None:
                if n_channels < 3:
                    colormap = colormaps.MAGENTA_GREEN
                else:
                    colormap = itertools.cycle(colormaps.CYMRGB)
            else:
                colormap = ensure_iterable(colormap)

            # If one pair of clim values is passed then need to iterate them to
            # all layers.
            if contrast_limits is not None and not is_iterable(
                contrast_limits[0]
            ):
                contrast_limits = itertools.repeat(contrast_limits)
            else:
                contrast_limits = ensure_iterable(contrast_limits)

            gamma = ensure_iterable(gamma)

            layer_list = []
            zipped_args = zip(
                range(n_channels), colormap, contrast_limits, gamma, name
            )
            for i, cmap, clims, _gamma, name in zipped_args:
                if is_pyramid:
                    image = [
                        np.take(data[j], i, axis=channel_axis)
                        for j in range(len(data))
                    ]
                else:
                    image = np.take(data, i, axis=channel_axis)
                layer = layers.Image(
                    image,
                    rgb=rgb,
                    colormap=cmap,
                    contrast_limits=clims,
                    gamma=_gamma,
                    interpolation=interpolation,
                    rendering=rendering,
                    name=name,
                    metadata=metadata,
                    scale=scale,
                    translate=translate,
                    opacity=opacity,
                    blending=blending,
                    visible=visible,
                )
                self.add_layer(layer)
                layer_list.append(layer)
            return layer_list