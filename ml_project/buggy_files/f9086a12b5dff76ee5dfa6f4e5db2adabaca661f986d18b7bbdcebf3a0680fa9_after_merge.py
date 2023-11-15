  def set_attribute(self, node, obj, name, value):
    """Set an attribute on an object.

    The attribute might already have a Variable in it and in that case we cannot
    overwrite it and instead need to add the elements of the new variable to the
    old variable.

    Args:
      node: The current CFG node.
      obj: The object.
      name: The name of the attribute to set.
      value: The Variable to store in it.
    Returns:
      A (possibly changed) CFG node.
    Raises:
      AttributeError: If the attribute cannot be set.
      NotImplementedError: If attribute setting is not implemented for obj.
    """
    if not self._check_writable(obj, name):
      # We ignore the write of an attribute that's not in __slots__, since it
      # wouldn't happen in the Python interpreter, either.
      return node
    assert isinstance(value, cfg.Variable)
    if self.vm.frame is not None and obj is self.vm.frame.f_globals:
      for v in value.data:
        v.update_official_name(name)
    if isinstance(obj, abstract.Empty):
      return node
    elif isinstance(obj, abstract.Module):
      # Assigning attributes on modules is pretty common. E.g.
      # sys.path, sys.excepthook.
      log.warning("Ignoring overwrite of %s.%s", obj.name, name)
      return node
    elif isinstance(obj, (abstract.StaticMethod, abstract.ClassMethod)):
      return self.set_attribute(node, obj.method, name, value)
    elif isinstance(obj, abstract.SimpleAbstractValue):
      return self._set_member(node, obj, name, value)
    elif isinstance(obj, abstract.BoundFunction):
      return self.set_attribute(node, obj.underlying, name, value)
    elif isinstance(obj, abstract.Unsolvable):
      return node
    elif isinstance(obj, abstract.Unknown):
      if name in obj.members:
        obj.members[name].PasteVariable(value, node)
      else:
        obj.members[name] = value.AssignToNewVariable(node)
      return node
    elif isinstance(obj, abstract.TypeParameterInstance):
      nodes = []
      for v in obj.instance.get_instance_type_parameter(obj.name).data:
        nodes.append(self.set_attribute(node, v, name, value))
      return self.vm.join_cfg_nodes(nodes) if nodes else node
    elif isinstance(obj, abstract.Union):
      for option in obj.options:
        node = self.set_attribute(node, option, name, value)
      return node
    else:
      raise NotImplementedError(obj.__class__.__name__)