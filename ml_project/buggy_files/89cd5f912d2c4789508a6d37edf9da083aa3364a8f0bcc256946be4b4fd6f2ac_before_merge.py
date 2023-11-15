    def __init__(self):
        super().__init__()
        self._register_load_state_dict_pre_hook(self._batch_shape_state_dict_hook)
        self.quadrature = GaussHermiteQuadrature1D()