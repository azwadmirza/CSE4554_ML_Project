    def __init__(self, mesh_id, filename, connectivity_indices,
                 connectivity_coords, index):
        self.field_data = YTFieldData()
        self.filename = filename
        self.field_parameters = {}
        self.mesh_id = mesh_id
        # This is where we set up the connectivity information
        self.connectivity_indices = connectivity_indices
        if connectivity_indices.shape[1] != self._connectivity_length:
            if self._connectivity_length == -1:
                self._connectivity_length = connectivity_indices.shape[1]
            else:
                raise RuntimeError
        self.connectivity_coords = connectivity_coords
        self.ds = index.dataset
        self._index = index
        self._last_mask = None
        self._last_count = -1
        self._last_selector_id = None
        self._current_particle_type = 'all'
        self._current_fluid_type = self.ds.default_fluid_type