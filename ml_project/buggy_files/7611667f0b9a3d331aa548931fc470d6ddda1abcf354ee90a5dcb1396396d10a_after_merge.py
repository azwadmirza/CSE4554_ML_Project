  def import_module(self, name, full_name, level):
    """Import a module and return the module object or None."""
    # Do not import new modules if we aren't in an IMPORT statement.
    # The exception is if we have an implicit "package" module (e.g.
    # `import a.b.c` adds `a.b` to the list of instantiable modules.)
    if not (self._importing or self.loader.has_module_prefix(full_name)):
      return None
    try:
      module = self._import_module(name, level)
      # Since we have explicitly imported full_name, add it to the prefix list.
      self.loader.add_module_prefixes(full_name)
    except (parser.ParseError, load_pytd.BadDependencyError,
            visitors.ContainerError, visitors.SymbolLookupError) as e:
      self.errorlog.pyi_error(self.frames, full_name, e)
      module = self.convert.unsolvable
    return module