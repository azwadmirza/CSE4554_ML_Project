    def _build(self):
        tensor = self._build_parameter()
        self._dataholder_tensor = tensor
        self._is_initialized_tensor = tf.is_variable_initialized(tensor)