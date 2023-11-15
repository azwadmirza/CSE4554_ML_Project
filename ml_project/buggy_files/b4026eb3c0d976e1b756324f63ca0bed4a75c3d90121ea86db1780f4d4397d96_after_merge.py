    def __init__(self, layer, node):
        super().__init__()

        self.layer = layer
        self.node = node
        self._position = (0,) * self.layer.dims.ndisplay
        self.camera = None

        self.layer.events.refresh.connect(lambda e: self.node.update())
        self.layer.events.set_data.connect(lambda e: self._on_data_change())

        self.layer.events.visible.connect(lambda e: self._on_visible_change())
        self.layer.events.opacity.connect(lambda e: self._on_opacity_change())
        self.layer.events.blending.connect(
            lambda e: self._on_blending_change()
        )
        self.layer.events.scale.connect(lambda e: self._on_scale_change())
        self.layer.events.translate.connect(
            lambda e: self._on_translate_change()
        )