    def prepare_variable(self, k, v, *args, **kwargs):
        new_var = Variable(v.dims, np.empty_like(v), v.attrs)
        # we copy the variable and stuff all encodings in the
        # attributes to imitate what happens when writing to disk.
        new_var.attrs.update(v.encoding)
        self._variables[k] = new_var
        return new_var, v.data