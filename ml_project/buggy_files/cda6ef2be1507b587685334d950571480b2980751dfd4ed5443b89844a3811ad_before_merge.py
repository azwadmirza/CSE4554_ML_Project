def import_func_from_source(source_path: Text, fn_name: Text) -> Callable:  # pylint: disable=g-bare-generic
  """Imports a function from a module provided as source file."""

  # If module path is not local, download to local file-system first,
  # because importlib can't import from GCS
  source_path = io_utils.ensure_local(source_path)

  try:
    if six.PY2:
      import imp  # pylint: disable=g-import-not-at-top
      try:
        user_module = imp.load_source('user_module', source_path)
        return getattr(user_module, fn_name)
      except IOError:
        raise

    else:
      loader = importlib.machinery.SourceFileLoader(
          fullname='user_module',
          path=source_path,
      )
      user_module = types.ModuleType(loader.name)
      loader.exec_module(user_module)
      return getattr(user_module, fn_name)

  except IOError:
    raise ImportError('{} in {} not found in import_func_from_source()'.format(
        fn_name, source_path))