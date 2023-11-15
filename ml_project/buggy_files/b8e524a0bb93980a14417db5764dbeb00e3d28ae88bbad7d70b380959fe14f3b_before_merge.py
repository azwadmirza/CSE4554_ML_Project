  def _modify_from_import_statements(self, red_baron):
    for from_import_node in red_baron.find_all('FromImportNode'):
      if self._skip(from_import_node):
        continue

      if len(from_import_node) == 0:
        # NB: `from . import ...` has length 0, but we don't care about relative imports which will
        # point back into vendored code if the origin is within vendored code.
        continue

      original = from_import_node.copy()
      root_package = from_import_node[0]
      if root_package.value in self._packages:
        root_package.replace('{prefix}.{root}'.format(prefix=self._prefix,
                                                      root=root_package.value))
        yield original, from_import_node