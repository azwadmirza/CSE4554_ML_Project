  def get_attribute(self, node, obj, name, valself=None):
    """Get the named attribute from the given object.

    Args:
      node: The current CFG node.
      obj: The object.
      name: The name of the attribute to retrieve.
      valself: A cfg.Binding to a self reference to include in the attribute's
        origins. If obj is a mixin.Class, valself can be a binding to:
        * an instance of obj - obj will be treated strictly as a class.
        * obj itself - obj will be treated as an instance of its metaclass.
        * None - if name == "__getitem__", obj is a type annotation; else, obj
            is strictly a class, but the attribute is left unbound.
        Else, valself is optional and should be a binding to obj when given.

    Returns:
      A tuple (CFGNode, cfg.Variable). If this attribute doesn't exist,
      the Variable will be None.
    """
    # Some objects have special attributes, like "__get__" or "__iter__"
    special_attribute = obj.get_special_attribute(node, name, valself)
    if special_attribute is not None:
      return node, special_attribute
    if isinstance(obj, abstract.Function):
      if name == "__get__":
        # The pytd for "function" has a __get__ attribute, but if we already
        # have a function we don't want to be treated as a descriptor.
        return node, None
      else:
        return self._get_instance_attribute(node, obj, name, valself)
    elif isinstance(obj, abstract.ParameterizedClass):
      return self.get_attribute(node, obj.base_cls, name, valself)
    elif isinstance(obj, mixin.Class):
      return self._get_class_attribute(node, obj, name, valself)
    elif isinstance(obj, overlay.Overlay):
      return self._get_module_attribute(
          node, obj.get_module(name), name, valself)
    elif isinstance(obj, abstract.Module):
      return self._get_module_attribute(node, obj, name, valself)
    elif isinstance(obj, abstract.SimpleAbstractValue):
      return self._get_instance_attribute(node, obj, name, valself)
    elif isinstance(obj, abstract.Union):
      nodes = []
      ret = self.vm.program.NewVariable()
      for o in obj.options:
        node2, attr = self.get_attribute(node, o, name, valself)
        if attr is not None:
          ret.PasteVariable(attr, node2)
          nodes.append(node2)
      if ret.bindings:
        return self.vm.join_cfg_nodes(nodes), ret
      else:
        return node, None
    elif isinstance(obj, special_builtins.SuperInstance):
      if obj.super_obj:
        cls = obj.super_cls
        valself = obj.super_obj.to_binding(node)
        skip = obj.super_cls
      else:
        cls = self.vm.convert.super_type
        skip = None
      return self._lookup_from_mro_and_handle_descriptors(
          node, cls, name, valself, skip)
    elif isinstance(obj, special_builtins.Super):
      return self.get_attribute(node, self.vm.convert.super_type, name, valself)
    elif isinstance(obj, abstract.BoundFunction):
      return self.get_attribute(node, obj.underlying, name, valself)
    elif isinstance(obj, abstract.TypeParameterInstance):
      param_var = obj.instance.get_instance_type_parameter(obj.name)
      if not param_var.bindings:
        param_var = obj.param.instantiate(self.vm.root_cfg_node)
      results = []
      nodes = []
      for v in param_var.data:
        node2, ret = self.get_attribute(node, v, name, valself)
        if ret is None:
          return node, None
        else:
          results.append(ret)
          nodes.append(node2)
      node = self.vm.join_cfg_nodes(nodes)
      return node, self.vm.join_variables(node, results)
    elif isinstance(obj, abstract.Empty):
      return node, None
    else:
      return node, None