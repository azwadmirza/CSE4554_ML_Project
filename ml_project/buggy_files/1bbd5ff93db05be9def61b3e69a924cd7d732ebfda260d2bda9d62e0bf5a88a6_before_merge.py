    def __init__(
        self,
        data,
        *,
        rgb=None,
        colormap='gray',
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
        blending='translucent',
        visible=True,
        multiscale=None,
    ):
        if isinstance(data, types.GeneratorType):
            data = list(data)

        # Determine if data is a multiscale
        if multiscale is None:
            multiscale = guess_multiscale(data)

        # Determine initial shape
        if multiscale:
            init_shape = data[0].shape
        else:
            init_shape = data.shape

        # Determine if rgb
        if rgb is None:
            rgb = guess_rgb(init_shape)

        # Determine dimensionality of the data
        if rgb:
            ndim = len(init_shape) - 1
        else:
            ndim = len(init_shape)

        super().__init__(
            data,
            ndim,
            name=name,
            metadata=metadata,
            scale=scale,
            translate=translate,
            opacity=opacity,
            blending=blending,
            visible=visible,
            multiscale=multiscale,
        )

        self.events.add(
            interpolation=Event,
            rendering=Event,
            iso_threshold=Event,
            attenuation=Event,
        )

        # Set data
        self.rgb = rgb
        self._data = data
        if self.multiscale:
            self._data_level = len(self.data) - 1
            # Determine which level of the multiscale to use for the thumbnail.
            # Pick the smallest level with at least one axis >= 64. This is
            # done to prevent the thumbnail from being from one of the very
            # low resolution layers and therefore being very blurred.
            big_enough_levels = [
                np.any(np.greater_equal(p.shape, 64)) for p in data
            ]
            if np.any(big_enough_levels):
                self._thumbnail_level = np.where(big_enough_levels)[0][-1]
            else:
                self._thumbnail_level = 0
        else:
            self._data_level = 0
            self._thumbnail_level = 0
        self.corner_pixels[1] = self.level_shapes[self._data_level]

        # Intitialize image views and thumbnails with zeros
        if self.rgb:
            self._data_view = np.zeros(
                (1,) * self.dims.ndisplay + (self.shape[-1],)
            )
        else:
            self._data_view = np.zeros((1,) * self.dims.ndisplay)
        self._data_raw = self._data_view
        self._data_thumbnail = self._data_view

        # Set contrast_limits and colormaps
        self._gamma = gamma
        self._iso_threshold = iso_threshold
        self._attenuation = attenuation
        if contrast_limits is None:
            self.contrast_limits_range = self._calc_data_range()
        else:
            self.contrast_limits_range = contrast_limits
        self._contrast_limits = tuple(self.contrast_limits_range)
        self.colormap = colormap
        self.contrast_limits = self._contrast_limits
        self._interpolation = {
            2: Interpolation.NEAREST,
            3: (
                Interpolation3D.NEAREST
                if self.__class__.__name__ == 'Labels'
                else Interpolation3D.LINEAR
            ),
        }
        self.interpolation = interpolation
        self.rendering = rendering

        # Trigger generation of view slice and thumbnail
        self._update_dims()