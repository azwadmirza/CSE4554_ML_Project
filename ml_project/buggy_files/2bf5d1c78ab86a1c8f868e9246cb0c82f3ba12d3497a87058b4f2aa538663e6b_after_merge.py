  def _store_value(self, state, name, value, local):
    if local:
      target = self.frame.f_locals
    else:
      target = self.frame.f_globals
    node = self.attribute_handler.set_attribute(state.node, target, name, value)
    if target is self.frame.f_globals and self.late_annotations:
      for annot in self.late_annotations[name]:
        annot.resolve(node, self.frame.f_globals, self.frame.f_locals)
    return state.change_cfg_node(node)