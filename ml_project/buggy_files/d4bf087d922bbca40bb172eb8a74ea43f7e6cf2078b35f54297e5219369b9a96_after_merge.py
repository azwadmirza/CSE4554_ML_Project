  def convert_annotations_list(self, node, annotations_list):
    """Convert a (name, raw_annot) list to a {name: annotation} dict."""
    annotations = {}
    for name, t in annotations_list:
      if t is None:
        continue
      annot = self._process_one_annotation(
          node, t, name, self.vm.simple_stack())
      if annot is not None:
        annotations[name] = annot
    return annotations