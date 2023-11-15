  def __init__(self, name, vm):
    """Basic initializer for all AtomicAbstractValues."""
    super(AtomicAbstractValue, self).__init__(vm)
    assert hasattr(vm, "program"), type(self)
    self.cls = None
    self.name = name
    self.mro = self.compute_mro()
    self.module = None
    self.official_name = None
    self.slots = None  # writable attributes (or None if everything is writable)
    # The template for the current class. It is usually a constant, lazily
    # loaded to accommodate recursive types, but in the case of typing.Generic
    # (only), it'll change every time when a new generic class is instantiated.
    self._template = None
    # names in the templates of the current class and its base classes
    self._all_template_names = None
    self._instance = None