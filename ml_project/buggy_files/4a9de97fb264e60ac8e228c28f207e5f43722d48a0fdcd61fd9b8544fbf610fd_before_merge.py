  def _load_formal_type_parameters(self):
    if self._formal_type_parameters_loaded:
      return
    if isinstance(self._formal_type_parameters,
                  abstract_utils.LazyFormalTypeParameters):
      formal_type_parameters = {}
      for name, param in self._raw_formal_type_parameters():
        if param is None:
          formal_type_parameters[name] = self.vm.convert.unsolvable
        else:
          formal_type_parameters[name] = self.vm.convert.constant_to_value(
              param, self._formal_type_parameters.subst, self.vm.root_cfg_node)
      self._formal_type_parameters = formal_type_parameters
    self._formal_type_parameters = (
        self.vm.annotations_util.convert_class_annotations(
            self.vm.root_cfg_node, self._formal_type_parameters))
    self._formal_type_parameters_loaded = True