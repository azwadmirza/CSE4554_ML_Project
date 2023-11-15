    def _var_to_pointer(self, var, hook_self):
        if var.grad is not None:
            self._var_to_pointer(var.grad, hook_self)

        var.data.old_set_(var.data.__class__(0))
        self.local_worker.register_object(hook_self.local_worker,
                                          obj=var.data,
                                          id=var.data.id,
                                          owners=var.owners,
                                          is_pointer=True)
        return var