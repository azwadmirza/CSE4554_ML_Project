    def __init__(self, id, filename=None, index=None):
        self.field_data = YTFieldData()
        self.field_parameters = {}
        self.id = id
        self._child_mask = self._child_indices = self._child_index_mask = None
        self.ds = index.dataset
        self._index = weakref.proxy(index)
        self.start_index = None
        self.filename = filename
        self._last_mask = None
        self._last_count = -1
        self._last_selector_id = None
        self._current_particle_type = 'all'
        self._current_fluid_type = self.ds.default_fluid_type