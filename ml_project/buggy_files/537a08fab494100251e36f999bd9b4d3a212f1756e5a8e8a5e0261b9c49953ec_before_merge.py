  def __init__(self, name, param_names, varargs_name, kwonly_params,
               kwargs_name, defaults, annotations, late_annotations, vm):
    """Create a SimpleFunction.

    Args:
      name: Name of the function as a string
      param_names: Tuple of parameter names as strings.
      varargs_name: The "args" in "*args". String or None.
      kwonly_params: Tuple of keyword-only parameters as strings. These do NOT
        appear in param_names.
      kwargs_name: The "kwargs" in "**kwargs". String or None.
      defaults: Dictionary of string names to values of default arguments.
      annotations: Dictionary of string names to annotations (strings or types).
      late_annotations: Dictionary of string names to string types, used for
        forward references or as-yet-unknown types.
      vm: The virtual machine for this function.
    """
    annotations = dict(annotations)
    late_annotations = dict(late_annotations)
    # Every parameter must have an annotation. Defaults to unsolvable.
    for n in itertools.chain(param_names, [varargs_name, kwargs_name],
                             kwonly_params):
      if n and n not in annotations and n not in late_annotations:
        annotations[n] = vm.convert.unsolvable
    if not isinstance(defaults, dict):
      defaults = dict(zip(param_names[-len(defaults):], defaults))
    signature = function.Signature(name, param_names, varargs_name,
                                   kwonly_params, kwargs_name, defaults,
                                   annotations, late_annotations)
    super(SimpleFunction, self).__init__(signature, vm)
    self.bound_class = BoundFunction