    def __init__(
        self, title='napari', ndisplay=2, order=None, axis_labels=None
    ):
        super().__init__()

        self.events = EmitterGroup(
            source=self,
            auto_connect=True,
            status=Event,
            help=Event,
            title=Event,
            interactive=Event,
            cursor=Event,
            reset_view=Event,
            active_layer=Event,
            palette=Event,
            grid=Event,
            layers_change=Event,
        )

        self.dims = Dims(
            ndim=None, ndisplay=ndisplay, order=order, axis_labels=axis_labels
        )

        self.layers = LayerList()

        self._status = 'Ready'
        self._help = ''
        self._title = title
        self._cursor = 'standard'
        self._cursor_size = None
        self._interactive = True
        self._active_layer = None
        self._grid_size = (1, 1)
        self.grid_stride = 1

        self._palette = None
        self.theme = 'dark'

        self.dims.events.camera.connect(self.reset_view)
        self.dims.events.ndisplay.connect(self._update_layers)
        self.dims.events.order.connect(self._update_layers)
        self.dims.events.axis.connect(self._update_layers)
        self.layers.events.changed.connect(self._on_layers_change)
        self.layers.events.changed.connect(self._update_active_layer)
        self.layers.events.changed.connect(self._update_grid)

        self.keymap_providers = [self]

        # Hold callbacks for when mouse moves with nothing pressed
        self.mouse_move_callbacks = []
        # Hold callbacks for when mouse is pressed, dragged, and released
        self.mouse_drag_callbacks = []
        self._persisted_mouse_event = {}
        self._mouse_drag_gen = {}