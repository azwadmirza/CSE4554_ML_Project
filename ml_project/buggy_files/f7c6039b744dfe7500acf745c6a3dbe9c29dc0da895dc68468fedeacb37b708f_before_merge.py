    def read_value(self, session=None):
        if session is not None:
            if not isinstance(session, tf.Session):
                raise ValueError('TensorFlow session expected as session argument.')
            is_built = self.is_built_coherence(session.graph)
            if is_built is Build.YES:
                return self._read_parameter_tensor(session)
        elif self._externally_defined:
            raise GPflowError('Externally defined parameter requires session.')
        return self._value