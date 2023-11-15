    def __init__(self, *args, **kwargs):
        scene.visuals.Line.__init__(self, *args, **kwargs)

        # initialize point markers
        self.markers = scene.visuals.Markers()
        self.marker_colors = np.ones((len(self.pos), 4), dtype=np.float32)
        self.markers.set_data(pos=self.pos, symbol="s", edge_color="red",
                              size=6)
        self.selected_point = None
        self.selected_index = -1
        # snap grid size
        self.gridsize = 10