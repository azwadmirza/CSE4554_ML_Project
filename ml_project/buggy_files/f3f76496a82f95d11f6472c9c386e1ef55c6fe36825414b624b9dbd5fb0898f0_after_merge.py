  def minimum_sys_modules(cls, site_libs, modules=None):
    """Given a set of site-packages paths, return a "clean" sys.modules.

    When importing site, modules within sys.modules have their __path__'s populated with
    additional paths as defined by *-nspkg.pth in site-packages, or alternately by distribution
    metadata such as *.dist-info/namespace_packages.txt.  This can possibly cause namespace
    packages to leak into imports despite being scrubbed from sys.path.

    NOTE: This method mutates modules' __path__ attributes in sys.modules, so this is currently an
    irreversible operation.
    """

    modules = modules or sys.modules
    new_modules = {}

    for module_name, module in modules.items():
      # Tainted modules should be dropped.
      module_file = getattr(module, '__file__', None)
      if module_file and cls._tainted_path(module_file, site_libs):
        TRACER.log('Dropping %s' % (module_name,), V=3)
        continue

      # Untainted non-packages (builtin modules) need no further special handling and can stay.
      if not hasattr(module, '__path__'):
        new_modules[module_name] = module
        continue

      # Unexpected objects, e.g. PEP 420 namespace packages, should just be dropped.
      if not isinstance(module.__path__, list):
        TRACER.log('Dropping %s' % (module_name,), V=3)
        continue

      # Drop tainted package paths.
      for k in reversed(range(len(module.__path__))):
        if cls._tainted_path(module.__path__[k], site_libs):
          TRACER.log('Scrubbing %s.__path__: %s' % (module_name, module.__path__[k]), V=3)
          module.__path__.pop(k)

      # The package still contains untainted path elements, so it can stay.
      if module.__path__:
        new_modules[module_name] = module

    return new_modules