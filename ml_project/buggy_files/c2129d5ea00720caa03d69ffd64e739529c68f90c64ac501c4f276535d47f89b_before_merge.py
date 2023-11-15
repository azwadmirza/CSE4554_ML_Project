  def init_annotation_var(self, node, name, var):
    """Instantiate a variable of an annotation, calling __init__."""
    try:
      typ = abstract_utils.get_atomic_value(var)
    except abstract_utils.ConversionError:
      error = "Type must be constant for variable annotation"
      self.vm.errorlog.invalid_annotation(self.vm.frames, None, error, name)
      return self.vm.new_unsolvable(node)
    else:
      if self.get_type_parameters(typ):
        self.vm.errorlog.not_supported_yet(
            self.vm.frames, "using type parameter in variable annotation")
        return self.vm.new_unsolvable(node)
      try:
        return self.init_annotation(node, typ, name, self.vm.frames)
      except self.LateAnnotationError:
        return abstract.LateAnnotation(typ, name, self.vm.simple_stack())