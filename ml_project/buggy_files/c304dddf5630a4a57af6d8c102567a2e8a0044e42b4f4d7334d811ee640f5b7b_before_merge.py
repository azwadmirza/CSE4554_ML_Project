    def __init__(self):
        scene.SceneCanvas.__init__(self, keys='interactive',
                                   size=(800, 800))

        # Create some initial points
        n = 7
        self.pos = np.zeros((n, 3), dtype=np.float32)
        self.pos[:, 0] = np.linspace(-50, 50, n)
        self.pos[:, 1] = np.random.normal(size=n, scale=10, loc=0)

        # create new editable line
        self.line = EditLineVisual(pos=self.pos, color='w', width=3,
                                   antialias=True, method='gl')

        self.view = self.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(rect=(-100, -100, 200, 200),
                                               aspect=1.0)
        # the left mouse button pan has to be disabled in the camera, as it
        # interferes with dragging line points
        # Proposed change in camera: make mouse buttons configurable
        self.view.camera._viewbox.events.mouse_move.disconnect(
            self.view.camera.viewbox_mouse_event)

        self.view.add(self.line)
        self.show()
        self.selected_point = None
        scene.visuals.GridLines(parent=self.view.scene)