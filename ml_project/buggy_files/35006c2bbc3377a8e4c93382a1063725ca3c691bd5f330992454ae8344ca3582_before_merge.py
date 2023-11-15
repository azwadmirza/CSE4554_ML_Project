  def _get_annotation(self, var, name):
    try:
      ret = abstract_utils.get_atomic_value(var, self._CLASS_TYPE)
      if isinstance(ret, abstract.AbstractOrConcreteValue):
        ret = abstract_utils.get_atomic_python_constant(var, six.string_types)
    except abstract_utils.ConversionError:
      raise TypeVarError("%s must be constant" % name)
    if not ret:
      raise TypeVarError("%s cannot be an empty string" % name)
    return ret