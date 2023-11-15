  def _modify_import_statements(self, red_baron):
    for import_node in red_baron.find_all('ImportNode'):
      if self._skip(import_node):
        continue

      original = import_node.copy()
      for index, import_module in enumerate(import_node):
        root_package = import_module[0]
        if root_package.value not in self._packages:
          continue

        # We need to handle 4 possible cases:
        # 1. a -> pex.third_party.a as a
        # 2. a.b -> pex.third_party.a.b, pex.third_party.a as a
        # 3. a as b -> pex.third_party.a as b
        # 4. a.b as c -> pex.third_party.a.b as c
        #
        # Of these, 2 is the interesting case. The code in question would be like:
        # ```
        # import a.b.c
        # ...
        # a.b.c.func()
        # ```
        # So we need to have imported `a.b.c` but also exposed the root of that package path, `a`
        # under the name expected by code. The import of the `a.b.c` leaf ensures all parent
        # packages have been imported (getting the middle `b` in this case which is not explicitly
        # imported). This ensures the code can traverse from the re-named root - `a` in this
        # example, through middle nodes (`a.b`) all the way to the leaf target (`a.b.c`).

        def prefixed_fullname():
          return '{prefix}.{module}'.format(prefix=self._prefix,
                                            module='.'.join(map(str, import_module)))

        if import_module.target:  # Cases 3 and 4.
          import_module.value = prefixed_fullname()
        else:
          if len(import_module) > 1:  # Case 2.
            import_node.insert(index, prefixed_fullname())

          # Cases 1 and 2.
          import_module.value = '{prefix}.{root}'.format(prefix=self._prefix,
                                                         root=root_package.value)
          import_module.target = root_package.value

        yield original, import_node