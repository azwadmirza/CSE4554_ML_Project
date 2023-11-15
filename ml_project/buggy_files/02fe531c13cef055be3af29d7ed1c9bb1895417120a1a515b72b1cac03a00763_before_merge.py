    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, frameon=False)
        self.fig.set_tight_layout(True)

        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(which='both', bottom=False, top=False, left=False, labelbottom=False, labelleft=False)
        self.axes.set_xlim(0, 1)
        self.axes.set_ylim(0, 1)
        self.axes.set_xticks([], [])
        self.axes.set_yticks([], [])
        self.axes.set_facecolor(COLOR_BACKGROUND)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        # User interaction
        self.fig.canvas.setFocusPolicy(Qt.ClickFocus)
        self.fig.canvas.setFocus()
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press_event)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release_event)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_drag_event)

        self.root_public_key = None
        self.token_balance = {}

        # Reference to nodes in the plotted graph
        self.root_node = None
        self.scatter_nodes = []

        self.graph = None
        self.pos = None
        self.old_pos = None
        self.node_positions = None
        self.redraw = False

        self.animation_frame = 0
        self.max_frames = 20
        self.translation = {'x': 0, 'y': 0}

        self.selected_node = {'public_key': '', 'up': 0, 'down': 0}
        self.node_selection_callback = None