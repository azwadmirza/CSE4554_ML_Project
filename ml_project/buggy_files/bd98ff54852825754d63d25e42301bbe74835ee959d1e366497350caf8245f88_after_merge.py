    def _var_to_pointer(self, var, hook_self):

        # recursively calls var_to_pointer in a depth first fashion
        # only recursive through variables (ignores .data)
        if var.grad is not None:
            self._var_to_pointer(var.grad, hook_self)

        # deletes local data (because now it's a pointer to remote data)
        var.data.old_set_(var.data.__class__(0))

        return var