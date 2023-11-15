def _get_monoid_reducer(monoid_op, x):
  aval = core.get_aval(x)
  if (type(aval) is ConcreteArray) and aval.shape == ():
    if monoid_op is add:
      return aval.val == 0 and _reduce_sum
    elif monoid_op is max:
      return aval.val == _get_max_identity(aval.dtype) and _reduce_max
    elif monoid_op is min:
      return aval.val == _get_min_identity(aval.dtype) and _reduce_min