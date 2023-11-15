def run_node(node: Node, catalog: DataCatalog) -> Node:
    """Run a single `Node` with inputs from and outputs to the `catalog`.

    Args:
        node: The ``Node`` to run.
        catalog: A ``DataCatalog`` containing the node's inputs and outputs.

    Returns:
        The node argument.

    """
    inputs = {name: catalog.load(name) for name in node.inputs}
    outputs = node.run(inputs)
    for name, data in outputs.items():
        catalog.save(name, data)
    return node