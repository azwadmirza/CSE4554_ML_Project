    def _unroll_param_dict(self, value_dict):
        unrolled_value_dict = {}
        for (param, value) in value_dict.items():
            if isinstance(param, ParameterExpression):
                unrolled_value_dict[param] = value
            if isinstance(param, ParameterVector):
                if not len(param) == len(value):
                    raise CircuitError('ParameterVector {} has length {}, which '
                                       'differs from value list {} of '
                                       'len {}'.format(param, len(param), value, len(value)))
                unrolled_value_dict.update(zip(param, value))
        return unrolled_value_dict