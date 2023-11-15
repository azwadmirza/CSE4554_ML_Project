  def call(self, node, _, args, alias_map=None):
    funcvar, name = args.posargs[0:2]
    if isinstance(args.namedargs, dict):
      kwargs = args.namedargs
    else:
      kwargs = self.vm.convert.value_to_constant(args.namedargs, dict)
    # TODO(mdemello): Check if there are any changes between python2 and
    # python3 in the final metaclass computation.
    # TODO(mdemello): Any remaining kwargs need to be passed to the metaclass.
    metaclass = kwargs.get("metaclass", None)
    if len(funcvar.bindings) != 1:
      raise abstract_utils.ConversionError(
          "Invalid ambiguous argument to __build_class__")
    func, = funcvar.data
    if not isinstance(func, InterpreterFunction):
      raise abstract_utils.ConversionError(
          "Invalid argument to __build_class__")
    func.is_class_builder = True
    bases = args.posargs[2:]

    node, _ = func.call(node, funcvar.bindings[0],
                        args.replace(posargs=(), namedargs={}),
                        new_locals=True)
    if func.last_frame:
      func.f_locals = func.last_frame.f_locals
      class_closure_var = func.last_frame.class_closure_var
    else:
      # We have hit 'maximum depth' before setting func.last_frame
      func.f_locals = self.vm.convert.unsolvable
      class_closure_var = None
    for base in bases:
      # If base class is NamedTuple, we will call its own make_class method to
      # make a class.
      base = abstract_utils.get_atomic_value(
          base, default=self.vm.convert.unsolvable)
      if isinstance(base, PyTDClass) and base.full_name == "typing.NamedTuple":
        # The subclass of NamedTuple will ignore all its base classes. This is
        # controled by a metaclass provided to NamedTuple.
        # See: https://github.com/python/typing/blob/master/src/typing.py#L2170
        return base.make_class(node, func.f_locals.to_variable(node))
    return node, self.vm.make_class(
        node, name, list(bases), func.f_locals.to_variable(node), metaclass,
        new_class_var=class_closure_var)