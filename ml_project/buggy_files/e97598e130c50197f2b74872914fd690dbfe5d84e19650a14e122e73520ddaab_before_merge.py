    def _build_parameter(self):
        if self._externally_defined:
            self._check_tensor_trainable(self.parameter_tensor)
            return self.parameter_tensor

        name = self._parameter_name()
        tensor = misc.get_variable_by_name(name)
        if tensor is not None:
            raise GPflowError('Tensor with name "{name}" already exists, {tensor}.'
                              .format(name=name, tensor=tensor))

        value = self._apply_transform(self._value)
        shape = value.shape if self.fixed_shape else None
        init = tf.placeholder(self.dtype, shape=shape, name='initial_unconstrained_value')
        self._initial_value_tensor = init
        if self.fixed_shape:
            return tf.get_variable(name, initializer=init, trainable=self.trainable)
        return tf.get_variable(name, initializer=init,
                               validate_shape=False,
                               trainable=self.trainable)