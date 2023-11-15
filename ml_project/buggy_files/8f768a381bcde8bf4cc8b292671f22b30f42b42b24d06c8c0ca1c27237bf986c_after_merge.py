    def _parse_returns(self, returns: Dict):

        assert returns[self.get_key()] == "ParameterList"

        self._function.returns_src().set_offset(returns["src"], self._function.slither)

        if self.is_compact_ast:
            returns = returns["parameters"]
        else:
            returns = returns[self.get_children("children")]

        for ret in returns:
            assert ret[self.get_key()] == "VariableDeclaration"
            local_var = self._add_param(ret)
            self._function.add_return(local_var.underlying_variable)