  def make_class(self, node, name_var, bases, class_dict_var, cls_var,
                 new_class_var=None):
    """Create a class with the name, bases and methods given.

    Args:
      node: The current CFG node.
      name_var: Class name.
      bases: Base classes.
      class_dict_var: Members of the class, as a Variable containing an
          abstract.Dict value.
      cls_var: The class's metaclass, if any.
      new_class_var: If not None, make_class() will return new_class_var with
          the newly constructed class added as a binding. Otherwise, a new
          variable if returned.

    Returns:
      A node and an instance of Class.
    """
    name = abstract_utils.get_atomic_python_constant(name_var)
    log.info("Declaring class %s", name)
    try:
      class_dict = abstract_utils.get_atomic_value(class_dict_var)
    except abstract_utils.ConversionError:
      log.error("Error initializing class %r", name)
      return self.convert.create_new_unknown(node)
    # Handle six.with_metaclass.
    metacls, bases = self._filter_out_metaclasses(bases)
    if metacls:
      cls_var = metacls
    # Flatten Unions in the bases
    bases = [self._process_base_class(node, base) for base in bases]
    if not bases:
      # Old style class.
      bases = [self.convert.oldstyleclass_type.to_variable(self.root_cfg_node)]
    if (isinstance(class_dict, abstract.Unsolvable) or
        not isinstance(class_dict, mixin.PythonConstant)):
      # An unsolvable appears here if the vm hit maximum depth and gave up on
      # analyzing the class we're now building. Otherwise, if class_dict isn't
      # a constant, then it's an abstract dictionary, and we don't have enough
      # information to continue building the class.
      var = self.new_unsolvable(node)
    else:
      if cls_var is None:
        cls_var = class_dict.members.get("__metaclass__")
        if cls_var and self.PY3:
          # This way of declaring metaclasses no longer works in Python 3.
          self.errorlog.ignored_metaclass(
              self.frames, name,
              cls_var.data[0].full_name if cls_var.bindings else "Any")
      if cls_var and all(v.data.full_name == "__builtin__.type"
                         for v in cls_var.bindings):
        cls_var = None
      # pylint: disable=g-long-ternary
      cls = abstract_utils.get_atomic_value(
          cls_var, default=self.convert.unsolvable) if cls_var else None
      try:
        val = abstract.InterpreterClass(
            name,
            bases,
            class_dict.pyval,
            cls,
            self)
        if class_dict.late_annotations:
          val.late_annotations = class_dict.late_annotations
          self.classes_with_late_annotations.append(val)
      except mro.MROError as e:
        self.errorlog.mro_error(self.frames, name, e.mro_seqs)
        var = self.new_unsolvable(node)
      except abstract_utils.GenericTypeError as e:
        self.errorlog.invalid_annotation(self.frames, e.annot, e.error)
        var = self.new_unsolvable(node)
      else:
        if new_class_var:
          var = new_class_var
        else:
          var = self.program.NewVariable()
        var.AddBinding(val, class_dict_var.bindings, node)
        node = val.call_metaclass_init(node)
        if not val.is_abstract:
          # Since a class decorator could have made the class inherit from
          # ABCMeta, we have to mark concrete classes now and check for
          # abstract methods at postprocessing time.
          self.concrete_classes.append((val, self.simple_stack()))
    self.trace_opcode(None, name, var)
    return node, var