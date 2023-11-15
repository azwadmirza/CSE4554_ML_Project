def base(net: network.TensorNetwork,
         algorithm: Callable[[List[Set[int]], Set[int], Dict[int, int]],
                             List]) -> network.TensorNetwork:
  """Base method for all `opt_einsum` contractors.

  Args:
    net: a TensorNetwork object. Should be connected.
    algorithm: `opt_einsum` contraction method to use.

  Returns:
    The network after full contraction.
  """
  net.check_connected()
  # First contract all trace edges
  edges = net.get_all_nondangling()
  for edge in edges:
    if edge in net and edge.is_trace():
      net.contract_parallel(edge)
  if not net.get_all_nondangling():
    # There's nothing to contract.
    return net

  # Then apply `opt_einsum`'s algorithm
  nodes = sorted(net.nodes_set)
  input_sets = utils.get_input_sets(net)
  output_set = utils.get_output_set(net)
  size_dict = utils.get_size_dict(net)
  path = algorithm(input_sets, output_set, size_dict)
  for a, b in path:
    new_node = nodes[a] @ nodes[b]
    nodes.append(new_node)
    nodes = utils.multi_remove(nodes, [a, b])
  return net