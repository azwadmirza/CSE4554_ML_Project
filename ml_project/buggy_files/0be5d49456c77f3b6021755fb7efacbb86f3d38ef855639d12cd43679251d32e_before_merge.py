  def call_init(self, node, instance):
    # Call __init__ on each binding.
    # TODO(kramm): This should do join_cfg_nodes, instead of concatenating them.
    for b in instance.bindings:
      if b.data in self._initialized_instances:
        continue
      self._initialized_instances.add(b.data)
      if isinstance(b.data, abstract.SimpleAbstractValue):
        for param in b.data.instance_type_parameters.values():
          node = self.call_init(node, param)
      node = self._call_method(node, b, "__init__")
      # Test classes initialize attributes in setUp() as well.
      cls = b.data.get_class()
      if isinstance(cls, abstract.InterpreterClass) and cls.is_test_class:
        node = self._call_method(node, b, "setUp")
    return node