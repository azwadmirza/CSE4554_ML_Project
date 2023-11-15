def _Visit(node, visitor, *args, **kwargs):
  """Visit the node."""
  name = type(visitor).__name__
  recursive = name in _visiting
  _visiting.add(name)

  start = metrics.get_cpu_clock()
  try:
    return _VisitNode(node, visitor, *args, **kwargs)
  finally:
    if not recursive:
      _visiting.remove(name)
      elapsed = metrics.get_cpu_clock() - start
      metrics.get_metric("visit_" + name, metrics.Distribution).add(elapsed)
      if _visiting:
        metrics.get_metric(
            "visit_nested_" + name, metrics.Distribution).add(elapsed)