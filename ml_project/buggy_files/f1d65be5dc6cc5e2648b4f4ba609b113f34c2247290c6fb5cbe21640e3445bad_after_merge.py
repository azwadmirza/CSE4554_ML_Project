  def _process_base_class(self, node, base):
    """Process a base class for InterpreterClass creation."""
    new_base = self.program.NewVariable()
    for b in base.bindings:
      base_val = b.data
      if isinstance(b.data, abstract.AnnotationContainer):
        base_val = base_val.base_cls
      # A class like `class Foo(List["Foo"])` would lead to infinite recursion
      # when instantiated because we attempt to recursively instantiate its
      # parameters, so we replace any late annotations with Any.
      # TODO(rechen): only replace the current class's name. We should keep
      # other late annotations in order to support things like:
      #   class Foo(List["Bar"]): ...
      #   class Bar: ...
      base_val = self.annotations_util.remove_late_annotations(base_val)
      if isinstance(base_val, abstract.Union):
        # Union[A,B,...] is a valid base class, but we need to flatten it into a
        # single base variable.
        for o in base_val.options:
          new_base.AddBinding(o, {b}, node)
      else:
        new_base.AddBinding(base_val, {b}, node)
    base = new_base
    if not any(isinstance(t, (mixin.Class, abstract.AMBIGUOUS_OR_EMPTY))
               for t in base.data):
      self.errorlog.base_class_error(self.frames, base)
    return base