    def build(self, input_shape):
        super(LayerNormLSTMCell, self).build(input_shape)
        norm_input_shape = [input_shape[0], self.units]
        self.kernel_norm.build(norm_input_shape)
        self.recurrent_norm.build(norm_input_shape)
        self.state_norm.build(norm_input_shape)