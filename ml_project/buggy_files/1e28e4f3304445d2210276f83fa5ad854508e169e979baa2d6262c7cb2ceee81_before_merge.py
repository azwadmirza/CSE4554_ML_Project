def reduce(operands: Array, init_values: Array, computation: Callable,
           dimensions: Sequence[int]) -> Array:
  """Wraps XLA's `Reduce
  <https://www.tensorflow.org/xla/operation_semantics#reduce>`_
  operator.
  """
  flat_operands, operand_tree = tree_util.tree_flatten(operands)
  flat_init_values, init_value_tree = tree_util.tree_flatten(init_values)
  if operand_tree != init_value_tree:
    raise ValueError('Operands must have the same tree structure as init_values:'
                     f' {operand_tree} vs. {init_value_tree}')
  if len(flat_operands) != len(flat_init_values):
    raise ValueError('Must have same total number of operands as init_values: '
                     f' {len(flat_operands)} vs. {len(flat_init_values)}')
  monoid_reducer = _get_monoid_reducer(computation, flat_init_values)
  if monoid_reducer:
    # monoid reducers bypass the weak_type_rule, so we set it explicitly.
    weak_type = dtypes.is_weakly_typed(*flat_operands) and dtypes.is_weakly_typed(*flat_init_values)
    return convert_element_type(monoid_reducer(*flat_operands, dimensions), weak_type=weak_type)
  else:
    flat_init_avals = safe_map(_abstractify, flat_init_values)
    # breakpoint()
    jaxpr, consts, out_tree = _variadic_reduction_jaxpr(
        computation, tuple(flat_init_avals), init_value_tree)
    out = reduce_p.bind(*(flat_operands + flat_init_values), computation=computation,
                         jaxpr=jaxpr, consts=consts, dimensions=tuple(dimensions))
    return tree_util.tree_unflatten(out_tree, out)