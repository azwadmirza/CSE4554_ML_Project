    def _parse_params(self, params: Dict):
        assert params[self.get_key()] == "ParameterList"

        self.parameters_src.set_offset(params["src"], self._function.slither)

        if self.is_compact_ast:
            params = params["parameters"]
        else:
            params = params[self.get_children("children")]

        for param in params:
            assert param[self.get_key()] == "VariableDeclaration"
            local_var = self._add_param(param)
            self._function.add_parameters(local_var.underlying_variable)