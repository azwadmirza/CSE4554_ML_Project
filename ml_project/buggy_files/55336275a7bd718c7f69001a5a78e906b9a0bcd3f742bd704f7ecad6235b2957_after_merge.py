  def update_module_paths(cls, new_code_path):
    # Force subsequent imports to come from the .pex directory rather than the .pex file.
    TRACER.log('Adding to the head of sys.path: %s' % new_code_path)
    sys.path.insert(0, new_code_path)
    for name, module in sys.modules.items():
      if hasattr(module, '__path__'):
        module_dir = os.path.join(new_code_path, *name.split("."))
        TRACER.log('Adding to the head of %s.__path__: %s' % (module.__name__, module_dir))
        try:
          module.__path__.insert(0, module_dir)
        except AttributeError:
          # TODO: This is a temporary bandaid for an unhandled AttributeError which results
          # in a startup crash. See https://github.com/pantsbuild/pex/issues/598 for more info.
          TRACER.log(
            'Failed to insert %s: %s.__path__ of type %s does not support insertion!' % (
              module_dir,
              module.__name__,
              type(module.__path__)
            )
          )