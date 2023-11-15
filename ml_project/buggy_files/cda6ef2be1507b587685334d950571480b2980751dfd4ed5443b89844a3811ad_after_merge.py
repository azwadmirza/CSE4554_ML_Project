def import_func_from_source(source_path: Text, fn_name: Text) -> Callable:  # pylint: disable=g-bare-generic
  """Imports a function from a module provided as source file."""

  # If module path is not local, download to local file-system first,
  # because importlib can't import from GCS
  source_path = io_utils.ensure_local(source_path)

  try:
    loader = importlib.machinery.SourceFileLoader(
        fullname='user_module',
        path=source_path,
    )
    spec = importlib.util.spec_from_loader(
        loader.name, loader, origin=source_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return getattr(module, fn_name)

  except IOError:
    raise ImportError('{} in {} not found in import_func_from_source()'.format(
        fn_name, source_path))