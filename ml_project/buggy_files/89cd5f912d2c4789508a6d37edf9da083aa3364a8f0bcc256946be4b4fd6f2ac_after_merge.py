    def __init__(self, max_plate_nesting=1):
        super().__init__()
        self._register_load_state_dict_pre_hook(self._batch_shape_state_dict_hook)
        self.max_plate_nesting = max_plate_nesting