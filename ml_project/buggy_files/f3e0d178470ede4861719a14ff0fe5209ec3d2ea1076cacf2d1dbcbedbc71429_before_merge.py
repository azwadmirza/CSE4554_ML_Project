  def _process_module(self, module_name, filename, ast):
    """Create a module from a loaded ast and save it to the loader cache.

    Args:
      module_name: The fully qualified name of the module being imported.
      filename: The file the ast was generated from.
      ast: The pytd.TypeDeclUnit representing the module.

    Returns:
      The ast (pytd.TypeDeclUnit) as represented in this loader.
    """
    module = Module(module_name, filename, ast)
    self._modules[module_name] = module
    try:
      module.ast = self._postprocess_pyi(module.ast)
      # Now that any imported TypeVar instances have been resolved, adjust type
      # parameters in classes and functions.
      module.ast = module.ast.Visit(visitors.AdjustTypeParameters())
      # Now we can fill in internal cls pointers to ClassType nodes in the
      # module. This code executes when the module is first loaded, which
      # happens before any others use it to resolve dependencies, so there are
      # no external pointers into the module at this point.
      module.ast.Visit(
          visitors.FillInLocalPointers({"": module.ast,
                                        module_name: module.ast}))
    except:
      # don't leave half-resolved modules around
      del self._modules[module_name]
      raise
    return module.ast