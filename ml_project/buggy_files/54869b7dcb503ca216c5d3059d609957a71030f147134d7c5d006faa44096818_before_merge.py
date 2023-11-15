  def apply_type_comment(self, state, op, name, value):
    """If there is a type comment for the op, return its value."""
    assert op is self.vm.frame.current_opcode
    if op.code.co_filename != self.vm.filename:
      return value
    if not op.type_comment:
      return value
    comment = op.type_comment
    frame = self.vm.frame
    try:
      var = abstract_utils.eval_expr(
          self.vm, state.node, frame.f_globals, frame.f_locals, comment)
    except abstract_utils.EvaluationError as e:
      self.vm.errorlog.invalid_type_comment(
          self.vm.frames, comment, details=e.details)
      value = self.vm.new_unsolvable(state.node)
    else:
      try:
        typ = abstract_utils.get_atomic_value(var)
      except abstract_utils.ConversionError:
        self.vm.errorlog.invalid_type_comment(
            self.vm.frames, comment, details="Must be constant.")
        value = self.vm.new_unsolvable(state.node)
      else:
        if self.get_type_parameters(typ):
          self.vm.errorlog.not_supported_yet(
              self.vm.frames, "using type parameter in type comment")
        try:
          value = self.init_annotation(state.node, typ, name, self.vm.frames)
        except self.LateAnnotationError:
          value = abstract.LateAnnotation(typ, name, self.vm.simple_stack())
    return value