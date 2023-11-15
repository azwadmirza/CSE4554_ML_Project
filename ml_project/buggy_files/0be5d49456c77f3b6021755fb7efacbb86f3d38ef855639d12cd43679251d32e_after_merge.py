  def call_init(self, node, instance):
    # Call __init__ on each binding.
    # TODO(kramm): This should do join_cfg_nodes, instead of concatenating them.
    for b in instance.bindings:
      if b.data in self._initialized_instances:
        continue
      self._initialized_instances.add(b.data)
      node = self._call_init_on_binding(node, b)
    return node