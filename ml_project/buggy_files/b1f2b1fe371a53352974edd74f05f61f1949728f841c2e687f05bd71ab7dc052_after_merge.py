def _device_put_impl(x, device=None):
  try:
    a = abstractify(x)
  except TypeError:
    raise TypeError("Argument '{}' of type {} is not a valid JAX type"
                    .format(x, type(x)))
  handler = aval_to_result_handler(device, a)
  return handler(device_put(x, device))