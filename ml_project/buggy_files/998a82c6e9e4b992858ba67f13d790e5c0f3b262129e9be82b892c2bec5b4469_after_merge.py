  def _process_one_annotation(self, node, annotation, name, stack, seen=None):
    """Change annotation / record errors where required."""
    # Make sure we pass in a frozen snapshot of the frame stack, rather than the
    # actual stack, since late annotations need to snapshot the stack at time of
    # creation in order to get the right line information for error messages.
    assert isinstance(stack, tuple), "stack must be an immutable sequence"

    # Check for recursive type annotations so we can emit an error message
    # rather than crashing.
    if seen is None:
      seen = set()
    if annotation.is_late_annotation():
      if annotation in seen:
        self.vm.errorlog.not_supported_yet(
            stack, "Recursive type annotations",
            details="In annotation '%s' on %s" % (annotation.expr, name))
        return None
      seen = seen | {annotation}

    if isinstance(annotation, abstract.AnnotationContainer):
      annotation = annotation.base_cls

    if isinstance(annotation, typing_overlay.Union):
      self.vm.errorlog.invalid_annotation(
          stack, annotation, "Needs options", name)
      return None
    elif (name is not None and name != "return"
          and isinstance(annotation, typing_overlay.NoReturn)):
      self.vm.errorlog.invalid_annotation(
          stack, annotation, "NoReturn is not allowed", name)
      return None
    elif isinstance(annotation, abstract.Instance) and (
        annotation.cls == self.vm.convert.str_type or
        annotation.cls == self.vm.convert.unicode_type
    ):
      # String annotations : Late evaluation
      if isinstance(annotation, mixin.PythonConstant):
        expr = annotation.pyval
        if not expr:
          self.vm.errorlog.invalid_annotation(
              stack, annotation, "Cannot be an empty string", name)
          return None
        frame = self.vm.frame
        try:
          # Immediately try to evaluate the reference, generating
          # LateAnnotation objects as needed. We don't store the entire string
          # as a LateAnnotation because:
          # - Starting in 3.8, or in 3.7 with __future__.annotations, all
          #   annotations look like forward references - most of them don't need
          #   to be late evaluated.
          # - Given an expression like "Union[str, NotYetDefined]", we want to
          #   evaluate the union immediately so we don't end up with a complex
          #   LateAnnotation, which can lead to bugs when instantiated.
          with self.vm.generate_late_annotations(stack):
            v = abstract_utils.eval_expr(
                self.vm, node, frame.f_globals, frame.f_locals, expr)
        except abstract_utils.EvaluationError as e:
          self.vm.errorlog.invalid_annotation(stack, annotation, e.details)
          return None
        if len(v.data) == 1:
          return self._process_one_annotation(
              node, v.data[0], name, stack, seen)
      self.vm.errorlog.invalid_annotation(
          stack, annotation, "Must be constant", name)
      return None
    elif annotation.cls == self.vm.convert.none_type:
      # PEP 484 allows to write "NoneType" as "None"
      return self.vm.convert.none_type
    elif isinstance(annotation, abstract.ParameterizedClass):
      for param_name, param in annotation.formal_type_parameters.items():
        processed = self._process_one_annotation(node, param, name, stack, seen)
        if processed is None:
          return None
        elif isinstance(processed, typing_overlay.NoReturn):
          self.vm.errorlog.invalid_annotation(
              stack, param, "NoReturn is not allowed as inner type", name)
          return None
        annotation.formal_type_parameters[param_name] = processed
      return annotation
    elif isinstance(annotation, abstract.Union):
      options = []
      for option in annotation.options:
        processed = self._process_one_annotation(
            node, option, name, stack, seen)
        if processed is None:
          return None
        elif isinstance(processed, typing_overlay.NoReturn):
          self.vm.errorlog.invalid_annotation(
              stack, option, "NoReturn is not allowed as inner type", name)
          return None
        options.append(processed)
      annotation.options = tuple(options)
      return annotation
    elif isinstance(annotation, (mixin.Class,
                                 abstract.AMBIGUOUS_OR_EMPTY,
                                 abstract.TypeParameter,
                                 typing_overlay.NoReturn)):
      return annotation
    else:
      self.vm.errorlog.invalid_annotation(stack, annotation, "Not a type", name)
      return None