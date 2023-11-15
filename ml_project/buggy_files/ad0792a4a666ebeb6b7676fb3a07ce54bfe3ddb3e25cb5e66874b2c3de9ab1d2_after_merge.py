  def convert_class_annotations(self, node, raw_annotations):
    """Convert a name -> raw_annot dict to annotations."""
    annotations = {}
    for name, t in raw_annotations.items():
      # Don't use the parameter name, since it's often something unhelpful
      # like `0`.
      annot = self._process_one_annotation(
          node, t, None, self.vm.simple_stack())
      annotations[name] = annot or self.vm.convert.unsolvable
    return annotations