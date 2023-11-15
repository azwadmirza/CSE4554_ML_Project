  def _instantiate_type(self, node, args, type_var):
    cls = self.vm.annotations_util.process_annotation_var(
        node, type_var, "attr.ib", self.vm.simple_stack())
    _, instance = self.vm.init_class(node, cls.data[0])
    return instance