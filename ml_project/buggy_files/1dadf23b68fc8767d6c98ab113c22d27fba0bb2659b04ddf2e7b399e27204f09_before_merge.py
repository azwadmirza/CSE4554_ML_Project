  def instantiate(self, node, container=None):
    if self.has_late_types():
      frame = self.vm.frame
      self.resolve_late_types(node, frame.f_globals, frame.f_locals)
    var = self.vm.program.NewVariable()
    if container and (not isinstance(container, SimpleAbstractValue) or
                      self.full_name in container.all_template_names):
      instance = TypeParameterInstance(self, container, self.vm)
      return instance.to_variable(node)
    else:
      for c in self.constraints:
        var.PasteVariable(c.instantiate(node, container))
      if self.bound:
        var.PasteVariable(self.bound.instantiate(node, container))
    if not var.bindings:
      var.AddBinding(self.vm.convert.unsolvable, [], node)
    return var