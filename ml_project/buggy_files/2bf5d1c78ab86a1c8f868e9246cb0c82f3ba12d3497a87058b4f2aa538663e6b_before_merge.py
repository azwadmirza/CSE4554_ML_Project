  def _store_value(self, state, name, value, local):
    if local:
      target = self.frame.f_locals
    else:
      target = self.frame.f_globals
    node = self.attribute_handler.set_attribute(state.node, target, name, value)
    return state.change_cfg_node(node)