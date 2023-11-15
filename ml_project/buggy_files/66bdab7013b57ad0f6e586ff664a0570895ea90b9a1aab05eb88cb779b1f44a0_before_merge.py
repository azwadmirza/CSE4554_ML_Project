def _dot_general_shape_rule(lhs, rhs, dimension_numbers):
  (lhs_contracting, rhs_contracting), (lhs_batch, rhs_batch) = dimension_numbers
  if len(lhs_batch) != len(rhs_batch):
    msg = ("dot_general requires equal numbers of lhs_batch and rhs_batch "
           "dimensions, got lhs_batch {} and rhs_batch {}.")
    raise TypeError(msg.format(lhs_batch, rhs_batch))
  if not onp.all(onp.equal(lhs_batch, rhs_batch)):
    msg = ("dot_general requires same lhs and rhs batch dimension numbers, "
           "got {} and {}.")
    raise TypeError(msg.format(lhs_batch, rhs_batch))
  lhs_batch_shape = onp.take(lhs.shape, lhs_batch)
  rhs_batch_shape = onp.take(rhs.shape, rhs_batch)
  if not onp.all(onp.equal(lhs_batch_shape, rhs_batch_shape)):
    msg = ("dot_general requires lhs batch dimensions and rhs batch dimensions "
           "to have the same shape, got {} and {}.")
    raise TypeError(msg.format(lhs_batch_shape, rhs_batch_shape))
  if tuple(sorted(lhs_batch)) != tuple(range(len(lhs_batch))):
    msg = ("dot_general requires lhs batch dimensions to precede contracting "
           "and non-contracting dimensions, got lhs_batch {}.")
    raise TypeError(msg.format(lhs_batch))
  if tuple(sorted(rhs_batch)) != tuple(range(len(rhs_batch))):
    msg = ("dot_general requires rhs batch dimensions to precede contracting "
           "and non-contracting dimensions, got rhs_batch {}.")
    raise TypeError(msg.format(rhs_batch))
  if not len(lhs_contracting) == len(rhs_contracting) == 1:
    msg = ("dot_general accepts exactly one lhs_contracting and "
           "rhs_contracting dimension, got {} and {}.")
    raise TypeError(msg.format(lhs_contracting, rhs_contracting))
  lhs_contracting_shape = onp.take(lhs.shape, lhs_contracting)
  rhs_contracting_shape = onp.take(rhs.shape, rhs_contracting)
  if not onp.all(onp.equal(lhs_contracting_shape, rhs_contracting_shape)):
    msg = ("dot_general requires contracting dimensions to have the same "
           "shape, got {} and {}.")
    raise TypeError(msg.format(lhs_contracting_shape, rhs_contracting_shape))
  if lhs.ndim > len(lhs_batch) + len(lhs_contracting) + 1:
    msg = ("dot_general requires either one or zero non-batch non-contracting "
           "lhs dimension, got {}.")
    diff = lhs.ndim - len(lhs_batch) - len(lhs_contracting)
    raise TypeError(msg.format(diff))
  if rhs.ndim > len(rhs_batch) + len(rhs_contracting) + 1:
    msg = ("dot_general requires either one or zero non-batch non-contracting "
           "rhs dimension, got {}.")
    diff = rhs.ndim - len(rhs_batch) - len(rhs_contracting)
    raise TypeError(msg.format(diff))

  batch_shape = tuple(onp.take(lhs.shape, lhs_batch))
  lhs_contract_or_batch = tuple(lhs_contracting) + tuple(lhs_batch)
  lhs_tensored_shape = tuple(onp.delete(lhs.shape, lhs_contract_or_batch))
  rhs_contract_or_batch = tuple(rhs_contracting) + tuple(rhs_batch)
  rhs_tensored_shape = tuple(onp.delete(rhs.shape, rhs_contract_or_batch))
  return batch_shape + lhs_tensored_shape + rhs_tensored_shape