  def _print_as_expected_type(self, t, instance=None):
    """Print abstract value t as a pytd type."""
    if t.is_late_annotation():
      return t.expr
    elif isinstance(t, (abstract.Unknown, abstract.Unsolvable, mixin.Class,
                        abstract.Union)):
      with t.vm.convert.pytd_convert.produce_detailed_output():
        return self._pytd_print(t.get_instance_type(instance=instance))
    elif (isinstance(t, mixin.PythonConstant) and
          not getattr(t, "could_contain_anything", False)):
      return re.sub(r"(\\n|\s)+", " ",
                    t.str_of_constant(self._print_as_expected_type))
    elif isinstance(t, abstract.AnnotationClass) or not t.cls:
      return t.name
    else:
      return "<instance of %s>" % self._print_as_expected_type(t.cls, t)