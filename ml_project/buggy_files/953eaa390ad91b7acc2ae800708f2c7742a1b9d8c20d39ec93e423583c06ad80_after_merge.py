  def byte_STORE_SUBSCR(self, state, op):
    """Implement obj[subscr] = val."""
    state, (val, obj, subscr) = state.popn(3)
    state = state.forward_cfg_node()
    if self._is_annotations_dict(obj):
      try:
        name = abstract_utils.get_atomic_python_constant(
            subscr, six.string_types)
      except abstract_utils.ConversionError:
        pass
      else:
        val = self.annotations_util.process_annotation_var(
            state.node, val, name, self.simple_stack())
        state = self._store_annotation(state, name, val)
    state = self.store_subscr(state, obj, subscr, val)
    return state