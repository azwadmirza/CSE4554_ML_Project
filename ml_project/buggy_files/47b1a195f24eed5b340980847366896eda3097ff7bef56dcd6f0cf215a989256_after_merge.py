  def call(self, node, func, args):
    if args.posargs:
      annot = self.vm.annotations_util.process_annotation_var(
          node, args.posargs[0], "typing.cast", self.vm.simple_stack())
      if any(t.formal for t in annot.data):
        self.vm.errorlog.invalid_typevar(
            self.vm.frames, "cannot pass a TypeVar to a function")
        return node, self.vm.new_unsolvable(node)
      return node, self.vm.annotations_util.init_annotation_var(
          node, "typing.cast", annot)
    return super(Cast, self).call(node, func, args)