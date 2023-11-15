    def read_value(self, session=None):
        if session is not None and not isinstance(session, tf.Session):
            raise ValueError('TensorFlow session expected as an argument.')
        if session is None and self._externally_defined:
            raise GPflowError('Externally defined parameter requires session.')
        elif session:
            is_built = self.is_built_coherence(session.graph)
            if is_built is Build.YES:
                return self._read_parameter_tensor(session)
        return self._value