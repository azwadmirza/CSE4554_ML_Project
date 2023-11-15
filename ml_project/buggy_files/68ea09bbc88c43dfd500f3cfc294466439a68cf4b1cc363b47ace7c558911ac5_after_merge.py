    def declare_builtin(self, name, pos):
        name = self.mangle_class_private_name(name)
        return self.outer_scope.declare_builtin(name, pos)