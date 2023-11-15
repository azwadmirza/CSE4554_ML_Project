  def convert_class_annotations(self, node, raw_annotations):
    """Convert a name -> raw_annot dict to annotations."""
    annotations = {}
    for name, t in raw_annotations.items():
      try:
        # Don't use the parameter name, since it's often something unhelpful
        # like `0`.
        annot = self._process_one_annotation(node, t, None, self.vm.frames)
      except self.LateAnnotationError:
        # Copy the late annotation back into the dict for
        # convert_function_annotations to deal with.
        # TODO(rechen): Handle it here so that the raw annotation isn't
        # accidentally used elsewhere.
        annotations[name] = t
      else:
        annotations[name] = annot or self.vm.convert.unsolvable
    return annotations