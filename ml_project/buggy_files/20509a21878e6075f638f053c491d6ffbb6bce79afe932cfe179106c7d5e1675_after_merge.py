  def update_module_paths(cls, pex_file, explode_dir):
    bootstrap = Bootstrap.locate()
    pex_path = os.path.realpath(pex_file)

    # Un-import any modules already loaded from within the .pex file.
    to_reimport = []
    for name, module in reversed(sorted(sys.modules.items())):
      if bootstrap.imported_from_bootstrap(module):
        TRACER.log('Not re-importing module %s from bootstrap.' % module, V=3)
        continue

      pkg_path = getattr(module, '__path__', None)
      if pkg_path and any(os.path.realpath(path_item).startswith(pex_path)
                          for path_item in pkg_path):
        sys.modules.pop(name)
        to_reimport.append((name, pkg_path, True))
      elif name != '__main__':  # The __main__ module is special in python and is not re-importable.
        mod_file = getattr(module, '__file__', None)
        if mod_file and os.path.realpath(mod_file).startswith(pex_path):
          sys.modules.pop(name)
          to_reimport.append((name, mod_file, False))

    # Force subsequent imports to come from the exploded .pex directory rather than the .pex file.
    TRACER.log('Adding to the head of sys.path: %s' % explode_dir)
    sys.path.insert(0, explode_dir)

    # And re-import them from the exploded pex.
    for name, existing_path, is_pkg in to_reimport:
      TRACER.log('Re-importing %s %s loaded via %r from exploded pex.'
                 % ('package' if is_pkg else 'module', name, existing_path))
      reimported_module = importlib.import_module(name)
      if is_pkg:
        for path_item in existing_path:
          # NB: It is not guaranteed that __path__ is a list, it may be a PEP-420 namespace package
          # object which supports a limited mutation API; so we append each item individually.
          reimported_module.__path__.append(path_item)