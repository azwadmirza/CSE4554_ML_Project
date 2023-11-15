  def __init__(self,
               base_module,
               python_version,
               pythonpath=(),
               imports_map=None,
               use_typeshed=True,
               modules=None):
    self._modules = modules or self._base_modules(python_version)
    if self._modules["__builtin__"].needs_unpickling():
      self._unpickle_module(self._modules["__builtin__"])
    if self._modules["typing"].needs_unpickling():
      self._unpickle_module(self._modules["typing"])
    self.builtins = self._modules["__builtin__"].ast
    self.typing = self._modules["typing"].ast
    self.base_module = base_module
    self.python_version = python_version
    self.pythonpath = pythonpath
    self.imports_map = imports_map
    self.use_typeshed = use_typeshed
    self._concatenated = None
    self._import_name_cache = {}  # performance cache
    self._aliases = {}
    # Paranoid verification that pytype.main properly checked the flags:
    if imports_map is not None:
      assert pythonpath == [""], pythonpath