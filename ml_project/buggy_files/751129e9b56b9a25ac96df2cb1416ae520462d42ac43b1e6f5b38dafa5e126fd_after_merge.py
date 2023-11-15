  def Bindings(self, viewpoint, strict=True):
    """Filters down the possibilities of bindings for this variable.

    It determines this by analyzing the control flow graph. Any definition for
    this variable that is invisible from the current point in the CFG is
    filtered out. This function differs from Filter() in that it only honors the
    CFG, not the source sets. As such, it's much faster.

    Arguments:
      viewpoint: The CFG node at which to determine the possible bindings.
      strict: Whether to allow approximations for speed.

    Returns:
      A filtered list of bindings for this variable.
    """
    if viewpoint is None or (not strict and len(self.bindings) == 1):
      return self.bindings

    num_bindings = len(self.bindings)
    result = set()
    seen = set()
    stack = [viewpoint]
    while stack:
      if len(result) == num_bindings:
        break
      node = stack.pop()
      seen.add(node)
      bindings = self._cfgnode_to_bindings.get(node)
      if bindings is not None:
        assert bindings, "empty binding list"
        result.update(bindings)
        # Don't expand this node - previous assignments to this variable will
        # be invisible, since they're overwritten here.
        continue
      else:
        stack.extend(set(node.incoming) - seen)
    return list(result)