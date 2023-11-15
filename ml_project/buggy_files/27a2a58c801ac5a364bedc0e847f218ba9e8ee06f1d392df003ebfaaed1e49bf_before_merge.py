def _xla_call_impl(fun, *args, **params):
  device = params['device']
  backend = params['backend']
  compiled_fun = _xla_callable(fun, device, backend, *map(abstractify, args))
  try:
    return compiled_fun(*args)
  except FloatingPointError:
    print("Invalid value encountered in the output of a jit function. "
          "Calling the de-optimized version.")
    return fun.call_wrapped(*args)  # probably won't return