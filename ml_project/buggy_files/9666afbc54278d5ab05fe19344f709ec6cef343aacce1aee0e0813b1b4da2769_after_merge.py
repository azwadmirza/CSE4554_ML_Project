  def byte_LOAD_METHOD(self, state, op):
    name = self.frame.f_code.co_names[op.arg]
    state, self_obj = state.pop()
    state, result = self.load_attr(state, self_obj, name)
    # https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD says that
    # this opcode should push two values onto the stack: either the unbound
    # method and its `self` or NULL and the bound method. However, pushing only
    # the bound method and modifying CALL_METHOD accordingly works in all cases
    # we've tested.
    return state.push(result)