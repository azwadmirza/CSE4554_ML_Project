  def import_module(self, name, full_name, level):
    try:
      module = self._import_module(name, level)
    except (parser.ParseError, load_pytd.BadDependencyError,
            visitors.ContainerError, visitors.SymbolLookupError) as e:
      self.errorlog.pyi_error(self.frames, full_name, e)
      module = self.convert.unsolvable
    return module