    def params(self, parameters):
        self._params = []
        for single_param in parameters:
            # example: u2(pi/2, sin(pi/4))
            if isinstance(single_param, (ParameterExpression)):
                self._params.append(single_param)
            # example: u3(0.1, 0.2, 0.3)
            elif isinstance(single_param, (int, float)):
                self._params.append(single_param)
            # example: Initialize([complex(0,1), complex(0,0)])
            elif isinstance(single_param, complex):
                self._params.append(single_param)
            # example: snapshot('label')
            elif isinstance(single_param, str):
                self._params.append(single_param)
            # example: Aer expectation_value_snapshot [complex, 'X']
            elif isinstance(single_param, list):
                self._params.append(single_param)
            # example: numpy.array([[1, 0], [0, 1]])
            elif isinstance(single_param, numpy.ndarray):
                self._params.append(single_param)
            elif isinstance(single_param, numpy.number):
                self._params.append(single_param.item())
            else:
                raise CircuitError("invalid param type {0} in instruction "
                                   "{1}".format(type(single_param), self.name))