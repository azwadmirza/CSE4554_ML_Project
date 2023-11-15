    def _parse_returns(self, returns):

        assert returns[self.get_key()] == 'ParameterList'

        if self.is_compact_ast:
            returns = returns['parameters']
        else:
            returns = returns[self.get_children('children')]

        for ret in returns:
            assert ret[self.get_key()] == 'VariableDeclaration'

            local_var = LocalVariableSolc(ret)

            local_var.set_function(self)
            local_var.set_offset(ret['src'], self.contract.slither)
            local_var.analyze(self)

            # see https://solidity.readthedocs.io/en/v0.4.24/types.html?highlight=storage%20location#data-location
            if local_var.location == 'default':
                local_var.set_location('memory')

            self._variables[local_var.name] = local_var
            self._returns.append(local_var)