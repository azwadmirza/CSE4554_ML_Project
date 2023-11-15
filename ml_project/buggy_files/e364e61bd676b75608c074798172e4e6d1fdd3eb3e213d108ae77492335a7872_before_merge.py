def _remove(event):
    """When a layer is removed, remove its viewer."""
    layers = event.source
    layer = event.item
    layer._order = 0
    layer._node.parent = None