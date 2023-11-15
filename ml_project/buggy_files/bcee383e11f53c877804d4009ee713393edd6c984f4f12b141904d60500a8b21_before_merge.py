  def _print_annot(self, name):
    if name in self.annotations:
      return _print(self.annotations[name])
    elif name in self.late_annotations:
      return repr(self.late_annotations[name].expr)
    else:
      return None