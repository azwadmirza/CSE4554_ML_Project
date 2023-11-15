    def build(self, input_shape):
        super(LayerNormLSTMCell, self).build(input_shape)
        self.kernel_norm.build([input_shape[0], self.units * 4])
        self.recurrent_norm.build([input_shape[0], self.units * 4])
        self.state_norm.build([input_shape[0], self.units])