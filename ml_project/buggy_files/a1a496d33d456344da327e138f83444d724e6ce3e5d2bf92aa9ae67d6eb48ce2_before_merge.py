  def call(self, node, _, args):
    """Call typing.TypeVar()."""
    try:
      param = self._get_typeparam(node, args)
    except TypeVarError as e:
      self.vm.errorlog.invalid_typevar(
          self.vm.frames, utils.message(e), e.bad_call)
      return node, self.vm.new_unsolvable(node)
    if param.has_late_types():
      self.vm.params_with_late_types.append((param, self.vm.simple_stack()))
    return node, param.to_variable(node)