    def __init__(self, id, filename=None, index=None):
        super(AMRGridPatch, self).__init__(index.dataset, None)
        self.id = id
        self._child_mask = self._child_indices = self._child_index_mask = None
        self.ds = index.dataset
        self._index = weakref.proxy(index)
        self.start_index = None
        self.filename = filename
        self._last_mask = None
        self._last_count = -1
        self._last_selector_id = None