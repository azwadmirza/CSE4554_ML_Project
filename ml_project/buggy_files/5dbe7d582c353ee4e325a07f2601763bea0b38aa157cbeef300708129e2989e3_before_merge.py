  def _instantiate_type(self, node, args, type_var):
    cls = type_var.data[0]
    try:
      return self.vm.annotations_util.init_annotation(node, cls, "attr.ib",
                                                      self.vm.frames)
    except self.vm.annotations_util.LateAnnotationError:
      return abstract.LateAnnotation(cls, "attr.ib", self.vm.simple_stack())