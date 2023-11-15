  def _process_one_annotation(self, node, annotation, name, stack,
                              f_globals=None, f_locals=None, seen=None):
    """Change annotation / record errors where required."""

    # Check for recursive type annotations so we can emit an error message
    # rather than crashing.
    if seen is None:
      seen = set()
    if isinstance(annotation, abstract.AbstractOrConcreteValue):
      if annotation in seen:
        self.vm.errorlog.not_supported_yet(
            stack, "Recursive type annotations",
            details="In annotation '%s' on %s" % (annotation.pyval, name))
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
        if f_globals is None:
          raise self.LateAnnotationError()
        else:
          try:
            v = abstract_utils.eval_expr(
                self.vm, node, f_globals, f_locals, annotation.pyval)
          except abstract_utils.EvaluationError as e:
            self.vm.errorlog.invalid_annotation(stack, annotation, e.details)
            return None
          if len(v.data) == 1:
            return self._process_one_annotation(
                node, v.data[0], name, stack, f_globals, f_locals, seen)
      self.vm.errorlog.invalid_annotation(
          stack, annotation, "Must be constant", name)
      return None
    elif annotation.cls == self.vm.convert.none_type:
      # PEP 484 allows to write "NoneType" as "None"
      return self.vm.convert.none_type
    elif isinstance(annotation, abstract.ParameterizedClass):
      for param_name, param in annotation.formal_type_parameters.items():
        processed = self._process_one_annotation(
            node, param, name, stack, f_globals, f_locals, seen)
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
            node, option, name, stack, f_globals, f_locals, seen)
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