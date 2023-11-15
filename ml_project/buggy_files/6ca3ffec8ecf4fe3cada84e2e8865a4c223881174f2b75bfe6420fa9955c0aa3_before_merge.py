  def byte_STORE_ANNOTATION(self, state, op):
    """Implementation of the STORE_ANNOTATION opcode."""
    state, annotations_var = self.load_local(state, "__annotations__")
    name = self.frame.f_code.co_names[op.arg]
    state, value = state.pop()
    state = self._store_annotation(state, name, value)
    name_var = self.convert.build_string(state.node, name)
    state = self.store_subscr(state, annotations_var, name_var, value)
    return self.store_local(state, "__annotations__", annotations_var)