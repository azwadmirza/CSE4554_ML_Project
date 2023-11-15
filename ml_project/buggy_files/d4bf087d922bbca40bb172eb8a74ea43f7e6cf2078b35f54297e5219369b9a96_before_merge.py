  def convert_annotations_list(self, node, annotations_list):
    """Convert a (name, raw_annot) list to annotations and late annotations."""
    annotations = {}
    late_annotations = {}
    for name, t in annotations_list:
      if t is None:
        continue
      try:
        annot = self._process_one_annotation(node, t, name, self.vm.frames)
      except self.LateAnnotationError:
        late_annotations[name] = abstract.LateAnnotation(
            t, name, self.vm.simple_stack())
      else:
        if annot is not None:
          annotations[name] = annot
    return annotations, late_annotations