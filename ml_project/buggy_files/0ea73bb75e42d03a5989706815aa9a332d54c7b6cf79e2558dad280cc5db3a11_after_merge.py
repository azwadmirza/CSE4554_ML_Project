    def _parse_params(self, params):
        assert params[self.get_key()] == 'ParameterList'

        if self.is_compact_ast:
            params = params['parameters']
        else:
            params = params[self.get_children('children')]

        for param in params:
            assert param[self.get_key()] == 'VariableDeclaration'

            local_var = LocalVariableSolc(param)

            local_var.set_function(self)
            local_var.set_offset(param['src'], self.contract.slither)
            local_var.analyze(self)

            # see https://solidity.readthedocs.io/en/v0.4.24/types.html?highlight=storage%20location#data-location
            if local_var.location == 'default':
                local_var.set_location('memory')

            self._add_local_variable(local_var)
            self._parameters.append(local_var)