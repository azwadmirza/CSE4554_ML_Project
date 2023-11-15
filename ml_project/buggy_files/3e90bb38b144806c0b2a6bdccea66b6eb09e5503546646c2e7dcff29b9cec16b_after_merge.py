    def __init__(
        self,
        data=None,
        *,
        properties=None,
        symbol='o',
        size=10,
        edge_width=1,
        edge_color='black',
        edge_color_cycle=None,
        edge_colormap='viridis',
        edge_contrast_limits=None,
        face_color='white',
        face_color_cycle=None,
        face_colormap='viridis',
        face_contrast_limits=None,
        n_dimensional=False,
        name=None,
        metadata=None,
        scale=None,
        translate=None,
        opacity=1,
        blending='translucent',
        visible=True,
    ):
        if data is None:
            data = np.empty((0, 2))
        else:
            data = np.atleast_2d(data)
        ndim = data.shape[1]
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
            mode=Event,
            size=Event,
            edge_width=Event,
            face_color=Event,
            current_face_color=Event,
            edge_color=Event,
            current_edge_color=Event,
            symbol=Event,
            n_dimensional=Event,
            highlight=Event,
        )
        # update highlights when the layer is selected/deselected
        self.events.select.connect(self._set_highlight)
        self.events.deselect.connect(self._set_highlight)

        self._colors = get_color_namelist()

        # Save the point coordinates
        self._data = np.asarray(data)
        self.dims.clip = False

        # Save the properties
        if properties is None:
            properties = {}
        elif not isinstance(properties, dict):
            properties = dataframe_to_properties(properties)
        self._properties = self._validate_properties(properties)

        # Save the point style params
        self.symbol = symbol
        self._n_dimensional = n_dimensional
        self.edge_width = edge_width

        # The following point properties are for the new points that will
        # be added. For any given property, if a list is passed to the
        # constructor so each point gets its own value then the default
        # value is used when adding new points
        if np.isscalar(size):
            self._current_size = np.asarray(size)
        else:
            self._current_size = 10

        # Indices of selected points
        self._selected_data = []
        self._selected_data_stored = []
        self._selected_data_history = []
        # Indices of selected points within the currently viewed slice
        self._selected_view = []
        # Index of hovered point
        self._value = None
        self._value_stored = None
        self._mode = Mode.PAN_ZOOM
        self._mode_history = self._mode
        self._status = self.mode
        self._highlight_index = []
        self._highlight_box = None

        self._drag_start = None

        # Nx2 array of points in the currently viewed slice
        self._data_view = np.empty((0, 2))
        # Sizes of points in the currently viewed slice
        self._size_view = 0
        # Full data indices of points located in the currently viewed slice
        self._indices_view = []

        self._drag_box = None
        self._drag_box_stored = None
        self._is_selecting = False
        self._clipboard = {}

        with self.block_update_properties():
            self.edge_color_property = ''
            self.edge_color = edge_color
            if edge_color_cycle is None:
                edge_color_cycle = DEFAULT_COLOR_CYCLE
            self.edge_color_cycle = edge_color_cycle
            self.edge_colormap = edge_colormap
            self._edge_contrast_limits = edge_contrast_limits

            self._face_color_property = ''
            self.face_color = face_color
            if face_color_cycle is None:
                face_color_cycle = DEFAULT_COLOR_CYCLE
            self.face_color_cycle = face_color_cycle
            self.face_colormap = face_colormap
            self._face_contrast_limits = face_contrast_limits

        self.refresh_colors()

        # set the current_* properties
        self._current_edge_color = self.edge_color[-1]
        self._current_face_color = self.face_color[-1]
        self.size = size
        self.current_properties = {
            k: np.asarray([v[-1]]) for k, v in self.properties.items()
        }

        # Trigger generation of view slice and thumbnail
        self._update_dims()