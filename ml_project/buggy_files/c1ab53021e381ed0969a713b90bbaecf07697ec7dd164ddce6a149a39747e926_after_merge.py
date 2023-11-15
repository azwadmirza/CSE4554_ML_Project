  def make(cls, name, code, f_locals, f_globals, defaults, kw_defaults, closure,
           annotations, vm):
    """Get an InterpreterFunction.

    Things like anonymous functions and generator expressions are created
    every time the corresponding code executes. Caching them makes it easier
    to detect when the environment hasn't changed and a function call can be
    optimized away.

    Arguments:
      name: Function name.
      code: A code object.
      f_locals: The locals used for name resolution.
      f_globals: The globals used for name resolution.
      defaults: Default arguments.
      kw_defaults: Default arguments for kwonly parameters.
      closure: The free variables this closure binds to.
      annotations: Function annotations. Dict of name -> AtomicAbstractValue.
      vm: VirtualMachine instance.

    Returns:
      An InterpreterFunction.
    """
    annotations = annotations or {}
    if "return" in annotations:
      # Check Generator/AsyncGenerator return type
      ret_type = annotations["return"]
      if code.has_generator():
        if not abstract_utils.matches_generator(ret_type):
          error = "Expected Generator, Iterable or Iterator"
          vm.errorlog.invalid_annotation(vm.frames, ret_type, error)
      elif code.has_async_generator():
        if not abstract_utils.matches_async_generator(ret_type):
          error = "Expected AsyncGenerator, AsyncIterable or AsyncIterator"
          vm.errorlog.invalid_annotation(vm.frames, ret_type, error)
    overloads = vm.frame.overloads[name]
    key = (name, code,
           abstract_utils.hash_all_dicts(
               (f_globals.members, set(code.co_names)),
               (f_locals.members,
                set(f_locals.members) - set(code.co_varnames)),
               ({key: vm.program.NewVariable([value], [], vm.root_cfg_node)
                 for key, value in annotations.items()}, None),
               (dict(enumerate(vm.program.NewVariable([f], [], vm.root_cfg_node)
                               for f in overloads)), None),
               (dict(enumerate(defaults)), None),
               (dict(enumerate(closure or ())), None)))
    if key not in cls._function_cache:
      cls._function_cache[key] = cls(
          name, code, f_locals, f_globals, defaults, kw_defaults, closure,
          annotations, overloads, vm)
    return cls._function_cache[key]