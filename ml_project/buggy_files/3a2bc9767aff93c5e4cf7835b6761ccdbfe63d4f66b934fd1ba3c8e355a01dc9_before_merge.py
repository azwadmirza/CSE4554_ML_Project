def _pval_to_result_handler(pval):
  pv, const = pval
  if pv is None:
    return lambda _: const
  else:
    return aval_to_result_handler(pv)