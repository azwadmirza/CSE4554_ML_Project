    def __init__(
        self,
        data,
        *,
        rgb=None,
        is_pyramid=None,
        colormap='gray',
        contrast_limits=None,
        interpolation='nearest',
        rendering='mip',
        name=None,
        metadata=None,
        scale=None,
        translate=None,
        opacity=1,
        blending='translucent',
        visible=True,
    ):
        if isinstance(data, types.GeneratorType):
            data = list(data)

        ndim, rgb, is_pyramid, data_pyramid = get_pyramid_and_rgb(
            data, pyramid=is_pyramid, rgb=rgb
        )

        super().__init__(
            ndim,
            name=name,
            metadata=metadata,
            scale=scale,
            translate=translate,
            opacity=opacity,
            blending=blending,
            visible=visible,
        )

        self.events.add(
            contrast_limits=Event,
            colormap=Event,
            interpolation=Event,
            rendering=Event,
        )

        # Set data
        self.is_pyramid = is_pyramid
        self.rgb = rgb
        self._data = data
        self._data_pyramid = data_pyramid
        self._top_left = np.zeros(ndim, dtype=int)
        if self.is_pyramid:
            self._data_level = len(data_pyramid) - 1
        else:
            self._data_level = 0

        # Intitialize image views and thumbnails with zeros
        if self.rgb:
            self._data_view = np.zeros(
                (1,) * self.dims.ndisplay + (self.shape[-1],)
            )
        else:
            self._data_view = np.zeros((1,) * self.dims.ndisplay)
        self._data_thumbnail = self._data_view

        # Set contrast_limits and colormaps
        self._colormap_name = ''
        self._contrast_limits_msg = ''
        if contrast_limits is None:
            if self.is_pyramid:
                input_data = self._data_pyramid[-1]
            else:
                input_data = self.data
            self._contrast_limits_range = calc_data_range(input_data)
        else:
            self._contrast_limits_range = contrast_limits
        self._contrast_limits = copy(self._contrast_limits_range)
        self.colormap = colormap
        self.contrast_limits = self._contrast_limits
        self.interpolation = interpolation
        self.rendering = rendering

        # Trigger generation of view slice and thumbnail
        self._update_dims()