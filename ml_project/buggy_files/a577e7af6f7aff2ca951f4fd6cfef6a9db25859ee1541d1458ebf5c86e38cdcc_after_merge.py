    def __init__(
        self,
        data,
        *,
        properties=None,
        graph=None,
        tail_width=2,
        tail_length=30,
        name=None,
        metadata=None,
        scale=None,
        translate=None,
        opacity=1,
        blending='additive',
        visible=True,
        colormap='turbo',
        color_by='track_id',
        colormaps_dict=None,
    ):

        # if not provided with any data, set up an empty layer in 2D+t
        if data is None:
            data = np.empty((0, 4))
        else:
            # convert data to a numpy array if it is not already one
            data = np.asarray(data)

        # in absence of properties make the default an empty dict
        if properties is None:
            properties = {}

        # set the track data dimensions (remove ID from data)
        ndim = data.shape[1] - 1

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
        )

        self.events.add(
            tail_width=Event,
            tail_length=Event,
            display_id=Event,
            display_tail=Event,
            display_graph=Event,
            color_by=Event,
            colormap=Event,
            properties=Event,
            rebuild_tracks=Event,
            rebuild_graph=Event,
        )

        # track manager deals with data slicing, graph building and properties
        self._manager = TrackManager()
        self._track_colors = None
        self._colormaps_dict = colormaps_dict or {}  # additional colormaps
        self._color_by = color_by  # default color by ID
        self._colormap = colormap

        # use this to update shaders when the displayed dims change
        self._current_displayed_dims = None

        # track display properties
        self.tail_width = tail_width
        self.tail_length = tail_length
        self.display_id = False
        self.display_tail = True
        self.display_graph = True

        # set the data, properties and graph
        self.data = data
        self.properties = properties
        self.graph = graph or {}

        self.color_by = color_by
        self.colormap = colormap

        self._update_dims()

        # reset the display before returning
        self._current_displayed_dims = None