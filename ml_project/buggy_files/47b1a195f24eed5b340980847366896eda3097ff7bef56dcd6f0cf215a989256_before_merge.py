  def call(self, node, func, args):
    if args.posargs:
      try:
        annot = self.vm.annotations_util.process_annotation_var(
            node, args.posargs[0], "typing.cast", self.vm.frames)
      except self.vm.annotations_util.LateAnnotationError:
        self.vm.errorlog.invalid_annotation(
            self.vm.frames, self.vm.merge_values(args.posargs[0].data),
            "Forward references not allowed in typing.cast.\n"
            "Consider switching to a type comment.")
        annot = self.vm.new_unsolvable(node)
      args = args.replace(posargs=(annot,) + args.posargs[1:])
    return super(Cast, self).call(node, func, args)