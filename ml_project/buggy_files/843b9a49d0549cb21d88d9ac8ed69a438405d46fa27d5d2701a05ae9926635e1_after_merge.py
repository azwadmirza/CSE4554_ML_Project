    def bind_function_type_variables(self,
                                     fun_type: CallableType, defn: Context) -> List[TypeVarDef]:
        """Find the type variables of the function type and bind them in our tvar_scope"""
        if not self.tvar_scope:
            return []  # We are in third pass, nothing new here
        if fun_type.variables:
            for var in fun_type.variables:
                var_expr = self.lookup(var.name, var).node
                assert isinstance(var_expr, TypeVarExpr)
                self.tvar_scope.bind(var.name, var_expr)
            return fun_type.variables
        typevars = self.infer_type_variables(fun_type)
        # Do not define a new type variable if already defined in scope.
        typevars = [(name, tvar) for name, tvar in typevars
                    if not self.is_defined_type_var(name, defn)]
        defs = []  # type: List[TypeVarDef]
        for name, tvar in typevars:
            if not self.tvar_scope.allow_binding(tvar.fullname()):
                self.fail("Type variable '{}' is bound by an outer class".format(name), defn)
            self.tvar_scope.bind(name, tvar)
            binding = self.tvar_scope.get_binding(tvar.fullname())
            assert binding is not None
            defs.append(binding)

        return defs