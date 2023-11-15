  def _build_value(self, node, raw_inner, ellipses):
    if self.base_cls.is_late_annotation():
      # A parameterized LateAnnotation should be converted to another
      # LateAnnotation to delay evaluation until the first late annotation is
      # resolved. We don't want to create a ParameterizedClass immediately
      # because (1) ParameterizedClass expects its base_cls to be a mixin.Class,
      # and (2) we have to postpone error-checking anyway so we might as well
      # postpone the entire evaluation.
      printed_params = []
      for i, param in enumerate(raw_inner):
        if i in ellipses:
          printed_params.append("...")
        else:
          printed_params.append(pytd_utils.Print(param.get_instance_type(node)))
      expr = "%s[%s]" % (self.base_cls.expr, ", ".join(printed_params))
      annot = LateAnnotation(expr, self.base_cls.stack, self.vm)
      self.vm.late_annotations[self.base_cls.expr].append(annot)
      return annot
    template, inner, abstract_class = self._get_value_info(raw_inner, ellipses)
    if self.base_cls.full_name == "typing.Generic":
      # Generic is unique in that parameterizing it defines a new template;
      # usually, the parameterized class inherits the base class's template.
      template_params = [
          param.with_module(self.base_cls.full_name) for param in inner]
    else:
      template_params = None
    if len(inner) != len(template):
      if not template:
        self.vm.errorlog.not_indexable(self.vm.frames, self.base_cls.name,
                                       generic_warning=True)
      else:
        # Use the unprocessed values of `template` and `inner` so that the error
        # message matches what the user sees.
        name = "%s[%s]" % (
            self.full_name, ", ".join(t.name for t in self.base_cls.template))
        error = "Expected %d parameter(s), got %d" % (
            len(self.base_cls.template), len(raw_inner))
        self.vm.errorlog.invalid_annotation(self.vm.frames, None, error, name)
    else:
      if len(inner) == 1:
        val, = inner
        # It's a common mistake to index tuple, not tuple().
        # We only check the "int" case, since string literals are allowed for
        # late annotations.
        # TODO(kramm): Instead of blacklisting only int, this should use
        # annotations_util.py to look up legal types.
        if isinstance(val, Instance) and val.cls == self.vm.convert.int_type:
          # Don't report this error again.
          inner = (self.vm.convert.unsolvable,)
          self.vm.errorlog.not_indexable(self.vm.frames, self.name)
    params = {name: inner[i] if i < len(inner) else self.vm.convert.unsolvable
              for i, name in enumerate(template)}

    # For user-defined generic types, check if its type parameter matches
    # its corresponding concrete type
    if isinstance(self.base_cls, InterpreterClass) and self.base_cls.template:
      for formal in self.base_cls.template:
        if (isinstance(formal, TypeParameter) and not formal.is_generic() and
            isinstance(params[formal.name], TypeParameter)):
          if formal.name != params[formal.name].name:
            self.vm.errorlog.not_supported_yet(
                self.vm.frames,
                "Renaming TypeVar `%s` with constraints or bound" % formal.name)
        else:
          root_node = self.vm.root_cfg_node
          actual = params[formal.name].instantiate(root_node)
          bad = self.vm.matcher.bad_matches(actual, formal, root_node)
          if bad:
            with self.vm.convert.pytd_convert.produce_detailed_output():
              combined = pytd_utils.JoinTypes(
                  view[actual].data.to_type(root_node, view=view)
                  for view in bad)
              formal = self.vm.annotations_util.sub_one_annotation(
                  root_node, formal, [{}])
              self.vm.errorlog.bad_concrete_type(
                  self.vm.frames, combined, formal.get_instance_type(root_node))
              return self.vm.convert.unsolvable

    try:
      return abstract_class(self.base_cls, params, self.vm, template_params)
    except abstract_utils.GenericTypeError as e:
      self.vm.errorlog.invalid_annotation(self.vm.frames, e.annot, e.error)
      return self.vm.convert.unsolvable