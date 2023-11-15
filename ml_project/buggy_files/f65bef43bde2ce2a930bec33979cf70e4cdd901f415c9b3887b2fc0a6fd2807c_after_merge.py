  def load_from(self, state, store, name, discard_concrete_values=False):
    """Load an item out of locals, globals, or builtins."""
    assert isinstance(store, abstract.SimpleAbstractValue)
    assert store.is_lazy
    store.load_lazy_attribute(name)
    bindings = store.members[name].Bindings(state.node)
    if not bindings:
      raise KeyError(name)
    ret = self.program.NewVariable()
    self._filter_none_and_paste_bindings(
        state.node, bindings, ret,
        discard_concrete_values=discard_concrete_values)
    return state, ret