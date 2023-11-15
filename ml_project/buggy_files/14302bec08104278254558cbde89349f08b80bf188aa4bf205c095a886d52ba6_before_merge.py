    def __init__(
        self,
        ndim,
        *,
        name=None,
        metadata=None,
        scale=None,
        translate=None,
        opacity=1,
        blending='translucent',
        visible=True,
    ):
        super().__init__()

        self.metadata = metadata or {}
        self._opacity = opacity
        self._blending = Blending(blending)
        self._visible = visible
        self._selected = True
        self._freeze = False
        self._status = 'Ready'
        self._help = ''
        self._cursor = 'standard'
        self._cursor_size = None
        self._interactive = True
        self._value = None
        self.scale_factor = 1

        self.dims = Dims(ndim)
        self._scale = scale or [1] * ndim
        self._translate = translate or [0] * ndim
        self._scale_view = np.ones(ndim)
        self._translate_view = np.zeros(ndim)
        self._translate_grid = np.zeros(ndim)
        self.coordinates = (0,) * ndim
        self._position = (0,) * self.dims.ndisplay
        self.is_pyramid = False
        self._editable = True

        self._thumbnail_shape = (32, 32, 4)
        self._thumbnail = np.zeros(self._thumbnail_shape, dtype=np.uint8)
        self._update_properties = True
        self._name = ''
        self.events = EmitterGroup(
            source=self,
            auto_connect=True,
            refresh=Event,
            set_data=Event,
            blending=Event,
            opacity=Event,
            visible=Event,
            select=Event,
            deselect=Event,
            scale=Event,
            translate=Event,
            data=Event,
            name=Event,
            thumbnail=Event,
            status=Event,
            help=Event,
            interactive=Event,
            cursor=Event,
            cursor_size=Event,
            editable=Event,
        )
        self.name = name

        self.events.data.connect(lambda e: self._set_editable())
        self.dims.events.ndisplay.connect(lambda e: self._set_editable())
        self.dims.events.order.connect(lambda e: self._set_view_slice())
        self.dims.events.ndisplay.connect(lambda e: self._update_dims())
        self.dims.events.order.connect(lambda e: self._update_dims())
        self.dims.events.axis.connect(lambda e: self._set_view_slice())

        self.mouse_move_callbacks = []
        self.mouse_drag_callbacks = []
        self._persisted_mouse_event = {}
        self._mouse_drag_gen = {}