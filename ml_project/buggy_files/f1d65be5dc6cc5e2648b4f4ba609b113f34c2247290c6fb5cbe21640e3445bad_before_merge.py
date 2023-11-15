  def _process_base_class(self, node, base):
    """Process a base class for InterpreterClass creation."""
    new_base = self.program.NewVariable()
    for b in base.bindings:
      if isinstance(b.data, abstract.AnnotationContainer):
        new_base.AddBinding(b.data.base_cls, {b}, node)
      elif isinstance(b.data, abstract.Union):
        # Union[A,B,...] is a valid base class, but we need to flatten it into a
        # single base variable.
        for o in b.data.options:
          new_base.AddBinding(o, {b}, node)
      else:
        new_base.AddBinding(b.data, {b}, node)
    base = new_base
    if not any(isinstance(t, (mixin.Class, abstract.AMBIGUOUS_OR_EMPTY))
               for t in base.data):
      self.errorlog.base_class_error(self.frames, base)
    return base