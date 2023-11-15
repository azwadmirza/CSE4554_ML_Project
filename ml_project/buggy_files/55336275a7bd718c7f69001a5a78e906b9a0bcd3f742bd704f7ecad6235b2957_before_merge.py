  def update_module_paths(cls, new_code_path):
    # Force subsequent imports to come from the .pex directory rather than the .pex file.
    TRACER.log('Adding to the head of sys.path: %s' % new_code_path)
    sys.path.insert(0, new_code_path)
    for name, module in sys.modules.items():
      if hasattr(module, "__path__"):
        module_dir = os.path.join(new_code_path, *name.split("."))
        TRACER.log('Adding to the head of %s.__path__: %s' % (module.__name__, module_dir))
        module.__path__.insert(0, module_dir)