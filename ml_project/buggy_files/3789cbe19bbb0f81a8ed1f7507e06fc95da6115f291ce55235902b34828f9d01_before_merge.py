    def infer_type(self, env):
        # FIXME: this is way too redundant with analyse_types()
        node = self.analyse_as_cimported_attribute_node(env, target=False)
        if node is not None:
            return node.entry.type
        node = self.analyse_as_type_attribute(env)
        if node is not None:
            return node.entry.type
        obj_type = self.obj.infer_type(env)
        self.analyse_attribute(env, obj_type=obj_type)
        if obj_type.is_builtin_type and self.type.is_cfunction:
            # special case: C-API replacements for C methods of
            # builtin types cannot be inferred as C functions as
            # that would prevent their use as bound methods
            return py_object_type
        elif self.entry and self.entry.is_cmethod:
            # special case: bound methods should not be inferred
            # as their unbound method types
            return py_object_type
        return self.type