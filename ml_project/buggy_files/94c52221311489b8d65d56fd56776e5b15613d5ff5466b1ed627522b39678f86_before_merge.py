  def __init__(self, name, code, f_locals, f_globals, defaults, kw_defaults,
               closure, annotations, late_annotations, overloads, vm):
    log.debug("Creating InterpreterFunction %r for %r", name, code.co_name)
    self.bound_class = BoundInterpreterFunction
    self.doc = code.co_consts[0] if code.co_consts else None
    self.code = code
    self.f_globals = f_globals
    self.f_locals = f_locals
    self.defaults = tuple(defaults)
    self.kw_defaults = kw_defaults
    self.closure = closure
    self._call_cache = {}
    self._call_records = []
    # TODO(b/78034005): Combine this and PyTDFunction.signatures into a single
    # way to handle multiple signatures that SignedFunction can also use.
    self._overloads = overloads
    self.has_overloads = bool(overloads)
    self.is_overload = False  # will be set by typing_overlay.Overload.call
    self.nonstararg_count = self.code.co_argcount
    if self.code.co_kwonlyargcount >= 0:  # This is usually -1 or 0 (fast call)
      self.nonstararg_count += self.code.co_kwonlyargcount
    signature = self._build_signature(name, annotations, late_annotations)
    super(InterpreterFunction, self).__init__(signature, vm)
    self.last_frame = None  # for BuildClass
    self._store_call_records = False
    if self.vm.PY3:
      self.is_class_builder = False  # Will be set by BuildClass.
    else:
      self.is_class_builder = self.code.has_opcode(opcodes.LOAD_LOCALS)