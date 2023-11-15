    def __init__(self, viewer):
        super().__init__()

        self.pool = QThreadPool()

        QCoreApplication.setAttribute(
            Qt.AA_UseStyleSheetPropagationInWidgetStyles, True
        )

        self.viewer = viewer
        self.dims = QtDims(self.viewer.dims)
        self.controls = QtControls(self.viewer)
        self.layers = QtLayerList(self.viewer.layers)
        self.layerButtons = QtLayerButtons(self.viewer)
        self.viewerButtons = QtViewerButtons(self.viewer)
        self.console = QtConsole({'viewer': self.viewer})

        # This dictionary holds the corresponding vispy visual for each layer
        self.layer_to_visual = {}

        if self.console.shell is not None:
            self.console.style().unpolish(self.console)
            self.console.style().polish(self.console)
            self.console.hide()
            self.viewerButtons.consoleButton.clicked.connect(
                lambda: self._toggle_console()
            )
        else:
            self.viewerButtons.consoleButton.setEnabled(False)

        self.canvas = SceneCanvas(keys=None, vsync=True)
        self.canvas.events.ignore_callback_errors = False
        self.canvas.events.draw.connect(self.dims.enable_play)
        self.canvas.native.setMinimumSize(QSize(200, 200))
        self.canvas.context.set_depth_func('lequal')

        self.canvas.connect(self.on_mouse_move)
        self.canvas.connect(self.on_mouse_press)
        self.canvas.connect(self.on_mouse_release)
        self.canvas.connect(self.on_key_press)
        self.canvas.connect(self.on_key_release)
        self.canvas.connect(self.on_draw)

        self.view = self.canvas.central_widget.add_view()
        self._update_camera()

        main_widget = QWidget()
        main_layout = QGridLayout()
        main_layout.setContentsMargins(15, 20, 15, 10)
        main_layout.addWidget(self.canvas.native, 0, 1, 3, 1)
        main_layout.addWidget(self.dims, 3, 1)
        main_layout.addWidget(self.controls, 0, 0)
        main_layout.addWidget(self.layerButtons, 1, 0)
        main_layout.addWidget(self.layers, 2, 0)
        main_layout.addWidget(self.viewerButtons, 3, 0)
        main_layout.setColumnStretch(1, 1)
        main_layout.setSpacing(10)
        main_widget.setLayout(main_layout)

        self.setOrientation(Qt.Vertical)
        self.addWidget(main_widget)
        if self.console.shell is not None:
            self.addWidget(self.console)

        self._last_visited_dir = str(Path.home())

        self._cursors = {
            'disabled': QCursor(
                QPixmap(':/icons/cursor/cursor_disabled.png').scaled(20, 20)
            ),
            'cross': Qt.CrossCursor,
            'forbidden': Qt.ForbiddenCursor,
            'pointing': Qt.PointingHandCursor,
            'standard': QCursor(),
        }

        self._update_palette(viewer.palette)

        self._key_release_generators = {}

        self.viewer.events.interactive.connect(self._on_interactive)
        self.viewer.events.cursor.connect(self._on_cursor)
        self.viewer.events.reset_view.connect(self._on_reset_view)
        self.viewer.events.palette.connect(
            lambda event: self._update_palette(event.palette)
        )
        self.viewer.layers.events.reordered.connect(self._reorder_layers)
        self.viewer.layers.events.added.connect(self._add_layer)
        self.viewer.layers.events.removed.connect(self._remove_layer)
        self.viewer.dims.events.camera.connect(
            lambda event: self._update_camera()
        )
        # stop any animations whenever the layers change
        self.viewer.events.layers_change.connect(lambda x: self.dims.stop())

        self.setAcceptDrops(True)