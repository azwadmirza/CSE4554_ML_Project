  def _print_annot(self, name):
    return _print(self.annotations[name]) if name in self.annotations else None