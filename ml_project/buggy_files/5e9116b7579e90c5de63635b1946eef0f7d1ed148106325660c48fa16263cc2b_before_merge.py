    def _update_variables(
        self,
        function: AnyFunctionDef,
        variable_def: ast.Name,
    ) -> None:
        """
        Increases the counter of local variables.

        What is treated as a local variable?
        Check ``TooManyLocalsViolation`` documentation.
        """
        function_variables = self.variables[function]
        if variable_def.id not in function_variables:
            if variable_def.id == UNUSED_VARIABLE:
                return

            parent = getattr(variable_def, 'parent', None)
            if isinstance(parent, self._not_contain_locals):
                return

            function_variables.append(variable_def.id)