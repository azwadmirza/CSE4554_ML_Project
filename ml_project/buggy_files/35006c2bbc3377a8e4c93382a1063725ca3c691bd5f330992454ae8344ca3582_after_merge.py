  def _get_annotation(self, node, var, name):
    with self.vm.errorlog.checkpoint() as record:
      retvar = self.vm.annotations_util.process_annotation_var(
          node, var, name, self.vm.simple_stack())
    if record.errors:
      raise TypeVarError("\n".join(error.message for error in record.errors))
    try:
      return abstract_utils.get_atomic_value(retvar)
    except abstract_utils.ConversionError:
      raise TypeVarError("%s must be constant" % name)